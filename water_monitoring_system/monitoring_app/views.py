from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from datetime import datetime, timedelta
import csv
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle

from .models import WaterQualityData
from .serializers import WaterQualityDataSerializer, UserSerializer
from django.contrib.auth.models import User

class WaterQualityDataViewSet(viewsets.ModelViewSet):
    queryset = WaterQualityData.objects.all()
    serializer_class = WaterQualityDataSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def get_queryset(self):
        # Filter by user_id if provided
        user_id = self.request.query_params.get('user_id')
        if user_id:
            return WaterQualityData.objects.filter(user_id=user_id)
        return WaterQualityData.objects.all()
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        # Get the latest entry for a specific user
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({"error": "user_id parameter is required"}, status=400)
        
        latest_data = WaterQualityData.objects.filter(user_id=user_id).order_by('-timestamp').first()
        if not latest_data:
            return Response({"error": "No data found for this user"}, status=404)
        
        serializer = self.get_serializer(latest_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def date_range(self, request):
        # Get data for a specific date range and user
        user_id = request.query_params.get('user_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not all([user_id, start_date, end_date]):
            return Response({"error": "user_id, start_date and end_date parameters are required"}, status=400)
        
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD"}, status=400)
        
        # Check if date range is valid (max 31 days)
        if (end_date - start_date).days > 31:
            return Response({"error": "Date range cannot exceed 31 days"}, status=400)
        
        # Get data for the date range
        data = WaterQualityData.objects.filter(
            user_id=user_id,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date', 'timestamp')
        
        serializer = self.get_serializer(data, many=True)
        return Response(serializer.data)

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

# Web views
@login_required
def dashboard(request):
    users = User.objects.all()
    return render(request, 'monitoring_app/dashboard.html', {'users': users})

@login_required
def live_status(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        latest_data = WaterQualityData.objects.filter(user=user).order_by('-timestamp').first()
        all_data = WaterQualityData.objects.filter(user=user).order_by('-timestamp')[:50]  # Show last 50 entries
        
        return render(request, 'monitoring_app/live_status.html', {
            'user': user,
            'latest_data': latest_data,
            'all_data': all_data
        })
    except User.DoesNotExist:
        return redirect('dashboard')

@login_required
def download_page(request, user_id):
    user = User.objects.get(id=user_id)
    return render(request, 'monitoring_app/download.html', {'user': user})

@login_required
def download_data(request, user_id):
    if request.method == 'POST':
        user = User.objects.get(id=user_id)
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        file_format = request.POST.get('format')
        
        # Get selected fields
        fields = []
        for field in ['ph', 'flow', 'total_flow', 'cod', 'bod', 'tss', 'daily_flow']:
            if request.POST.get(field):
                fields.append(field)
        
        if not fields:
            return redirect('download_page', user_id=user_id)
        
        # Convert string dates to datetime
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Validate date range
        if (end_date - start_date).days > 31:
            return redirect('download_page', user_id=user_id)
        
        # Get data
        data = WaterQualityData.objects.filter(
            user=user,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date', 'timestamp')
        
        # Create the response based on the file format
        if file_format == 'excel':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="water_quality_data_{start_date}_to_{end_date}.csv"'
            
            writer = csv.writer(response)
            header = ['Date', 'Time'] + [field.upper() for field in fields]
            writer.writerow(header)
            
            for item in data:
                row = [item.date.strftime('%Y-%m-%d'), item.timestamp.strftime('%H:%M:%S')]
                for field in fields:
                    row.append(getattr(item, field))
                writer.writerow(row)
            
            return response
        
        elif file_format == 'pdf':
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="water_quality_data_{start_date}_to_{end_date}.pdf"'
            
            buffer = io.BytesIO()
            p = canvas.Canvas(buffer, pagesize=letter)
            
            # Set up the document
            p.setTitle(f"Water Quality Data for {user.username}")
            p.drawString(100, 750, f"Water Quality Data for {user.username}")
            p.drawString(100, 730, f"Date Range: {start_date} to {end_date}")
            
            # Create the table data
            table_data = [['Date', 'Time'] + [field.upper() for field in fields]]
            
            for item in data:
                row = [item.date.strftime('%Y-%m-%d'), item.timestamp.strftime('%H:%M:%S')]
                for field in fields:
                    row.append(str(getattr(item, field)))
                table_data.append(row)
            
            # Create the table
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            # Draw the table
            table.wrapOn(p, 400, 600)
            table.drawOn(p, 72, 600)
            
            p.showPage()
            p.save()
            
            pdf = buffer.getvalue()
            buffer.close()
            response.write(pdf)
            
            return response
    
    return redirect('download_page', user_id=user_id)