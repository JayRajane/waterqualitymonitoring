from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from datetime import datetime, timedelta
from django.utils import timezone
import csv
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from django.http import JsonResponse
from .models import WaterQualityData
from .serializers import WaterQualityDataSerializer, UserSerializer
from django.contrib.auth.models import User
from django.contrib.auth import logout
from reportlab.lib.colors import HexColor
from django.utils import timezone
from django.contrib import messages  # If using messages



class WaterQualityDataViewSet(viewsets.ModelViewSet):
    queryset = WaterQualityData.objects.all()
    serializer_class = WaterQualityDataSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def get_queryset(self):
        queryset = WaterQualityData.objects.all()
    
        # Filter by user_id if provided
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
    
        # Limit results if requested
        limit = self.request.query_params.get('limit')
        if limit and limit.isdigit():
            queryset = queryset.order_by('-timestamp')[:int(limit)]
        else:
            queryset = queryset.order_by('-timestamp')
    
        return queryset

    
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
        time_interval = request.query_params.get('time_interval', '0')  # Default to 0 (no interval)
    
        if not all([user_id, start_date, end_date]):
            return Response({"error": "user_id, start_date and end_date parameters are required"}, status=400)
    
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            time_interval = int(time_interval)
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD"}, status=400)
    
        # Check if date range is valid (max 31 days)
        if (end_date - start_date).days > 31:
            return Response({"error": "Date range cannot exceed 31 days"}, status=400)
    
        # Get data for the date range
        queryset = WaterQualityData.objects.filter(
            user_id=user_id,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('timestamp')
    
        # Apply time interval filtering if requested
        if time_interval > 0:
            # Convert minutes to seconds for comparison
            interval_seconds = time_interval * 60
        
            filtered_data = []
            last_timestamp = None
        
            for item in queryset:
                if last_timestamp is None:
                    filtered_data.append(item)
                    last_timestamp = item.timestamp
                else:
                    time_diff = (item.timestamp - last_timestamp).total_seconds()
                    if time_diff >= interval_seconds:
                        filtered_data.append(item)
                        last_timestamp = item.timestamp
        
            queryset = filtered_data
    
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


def custom_logout(request):
    logout(request)
    return redirect('login')

def logout_confirm(request):
    if request.method == 'POST':
        if 'confirm' in request.POST:  # If "Yes" was clicked
            logout(request)
            return redirect('login')
        else:  # If "No" was clicked
            return redirect('dashboard')
    return render(request, 'monitoring_app/logout_confirm.html')
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
def add_data(request):
    users = User.objects.all()
    return render(request, 'monitoring_app/add_data.html', {'users': users})

@login_required
def data_entry(request):
    users = User.objects.all()
    return render(request, 'monitoring_app/data_entry.html', {'users': users})

@login_required
def user_list(request):
    users = User.objects.all()
    user_data = [{'id': user.id, 'username': user.username} for user in users]
    return JsonResponse(user_data, safe=False)

@login_required
def water_quality_data(request):
    user_id = request.GET.get('user_id')
    limit = request.GET.get('limit', 20)
    
    queryset = WaterQualityData.objects.all()
    if user_id:
        queryset = queryset.filter(user_id=user_id)
    
    queryset = queryset.order_by('-timestamp')[:int(limit)]
    data = list(queryset.values('id', 'user_id', 'timestamp', 'ph', 'flow', 'daily_flow','total_flow', 'cod', 'bod', 'tss',  'date'))
    
    return JsonResponse(data, safe=False)

@login_required
def download_data(request, user_id):
    if request.method == 'POST':
        try:
            user = User.objects.get(id=user_id)
            start_date_str = request.POST.get('start_date')
            end_date_str = request.POST.get('end_date')
            file_format = request.POST.get('format')
            time_interval = int(request.POST.get('time_interval', 0))
            
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
            if (end_date - start_date).days > 31:
                messages.error(request, "Date range cannot exceed 31 days")
                return redirect('download_page', user_id=user_id)
            
            queryset = WaterQualityData.objects.filter(
                user=user,
                date__gte=start_date,
                date__lte=end_date
            ).order_by('timestamp')
            
            # Apply time interval filtering if requested
            if time_interval > 0:
                interval_seconds = time_interval * 60
                filtered_data = []
                last_timestamp = None
                
                # Evaluate the queryset to a list to avoid multiple DB hits
                data_list = list(queryset)
                
                for item in data_list:
                    if last_timestamp is None:
                        filtered_data.append(item)
                        last_timestamp = item.timestamp
                    else:
                        time_diff = (item.timestamp - last_timestamp).total_seconds()
                        if time_diff >= interval_seconds:
                            filtered_data.append(item)
                            last_timestamp = item.timestamp
                
                # Use the filtered data
                data = filtered_data
            else:
                data = list(queryset)
            
            # Get selected fields
            fields = []
            for field in ['ph', 'flow', 'daily_flow', 'total_flow', 'cod', 'bod', 'tss']:
                if request.POST.get(field):
                    fields.append(field)
            
            if not fields:
                messages.error(request, "Please select at least one parameter")
                return redirect('download_page', user_id=user_id)
            
            # Create the response based on the file format
            if file_format == 'excel':
                import openpyxl
                from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
                
                # Create a workbook and select the active worksheet
                wb = openpyxl.Workbook()
                ws = wb.active
                ws.title = "WATER QUALITY OF DATA"
                
                # Style configurations
                header_font = Font(bold=True, color="FFFFFF")
                header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
                centered_alignment = Alignment(horizontal="center", vertical="center")
                border = Border(
                    left=Side(border_style="thin", color="000000"),
                    right=Side(border_style="thin", color="000000"),
                    top=Side(border_style="thin", color="000000"),
                    bottom=Side(border_style="thin", color="000000")
                )
                
                # Add header row
                header = ['Date', 'Time'] + [field.upper() for field in fields]
                for col_num, column_title in enumerate(header, 1):
                    cell = ws.cell(row=1, column=col_num, value=column_title)
                    cell.font = header_font
                    cell.fill = header_fill
                    cell.alignment = centered_alignment
                    cell.border = border
                    
                    # Adjust column width to fit content
                    ws.column_dimensions[openpyxl.utils.get_column_letter(col_num)].width = max(12, len(column_title) + 4)
                
                # Add data rows
                row_fill = PatternFill(start_color="E9EDF4", end_color="E9EDF4", fill_type="solid")
                alt_row_fill = PatternFill(start_color="D3DFEE", end_color="D3DFEE", fill_type="solid")
                
                for row_num, item in enumerate(data, 2):
                    # Apply alternating row colors
                    row_color = row_fill if row_num % 2 == 0 else alt_row_fill
                    
                    # Date column
                    date_cell = ws.cell(row=row_num, column=1, value=item.date.strftime('%Y-%m-%d'))
                    date_cell.alignment = centered_alignment
                    date_cell.border = border
                    date_cell.fill = row_color
                    
                    # Time column
                    localized_timestamp = timezone.localtime(item.timestamp)
                    time_string = localized_timestamp.strftime('%H:%M:%S')
                    time_cell = ws.cell(row=row_num, column=2, value=time_string)
                    time_cell.alignment = centered_alignment
                    time_cell.border = border
                    time_cell.fill = row_color
                    time_cell.number_format = '@'  # Text format
                    
                    # Data columns
                    for col_num, field in enumerate(fields, 3):
                        cell = ws.cell(row=row_num, column=col_num, value=getattr(item, field))
                        cell.alignment = centered_alignment
                        cell.border = border
                        cell.fill = row_color
                
                # Create the response
                response = HttpResponse(
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = f'attachment; filename="water_quality_data_{start_date}_to_{end_date}.xlsx"'
                
                # Save the workbook to the response
                wb.save(response)
                
                return response
            
            elif file_format == 'pdf':
                from reportlab.pdfgen import canvas
                from reportlab.lib.pagesizes import letter
                from reportlab.lib import colors
                from reportlab.lib.colors import HexColor
                from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer
                from reportlab.lib.styles import getSampleStyleSheet
                from reportlab.lib.units import inch
    
                response = HttpResponse(content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="water_quality_data_{start_date}_to_{end_date}.pdf"'
    
                buffer = io.BytesIO()
    
                # Use SimpleDocTemplate to handle pagination automatically
                doc = SimpleDocTemplate(buffer, pagesize=letter, 
                           rightMargin=0.5*inch, leftMargin=0.5*inch,
                           topMargin=0.75*inch, bottomMargin=0.75*inch)
    
                # Create elements list to build document
                elements = []
    
                # Add title and date range
                styles = getSampleStyleSheet()
                title = Paragraph(f"Water Quality Data for {user.username}", styles['Title'])
                date_range = Paragraph(f"Date Range: {start_date} to {end_date}", styles['Normal'])
                elements.append(title)
                elements.append(date_range)
                elements.append(Spacer(1, 0.25*inch))
    
                # Create the table data
                table_data = [['Date', 'Time'] + [field.upper() for field in fields]]
    
                for item in data:
                    localized_timestamp = timezone.localtime(item.timestamp)
                    row = [item.date.strftime('%Y-%m-%d'), localized_timestamp.strftime('%H:%M:%S')]
                    for field in fields:
                        row.append(str(getattr(item, field)))
                    table_data.append(row)
    
                # Create the table with some auto-width
                table = Table(table_data, repeatRows=1)  # repeatRows=1 makes header repeat on each page
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), HexColor('#0096FF')),  # Custom blue color
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
    
                elements.append(table)
    
                # Build the document with all elements
                doc.build(elements)
    
                pdf = buffer.getvalue()
                buffer.close()
                response.write(pdf)
    
                return response
            
        except User.DoesNotExist:
            messages.error(request, "User not found")
            return redirect('download_page', user_id=user_id)
        except ValueError as e:
            messages.error(request, f"Invalid date format: {str(e)}")
            return redirect('download_page', user_id=user_id)
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('download_page', user_id=user_id)
    
    return redirect('download_page', user_id=user_id)
@login_required
def submit_data(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        
        try:
            user = User.objects.get(id=user_id)
            
            # Get data from form (use None for empty fields)
            ph = request.POST.get('ph', '') or None
            flow = request.POST.get('flow', '') or None
            cod = request.POST.get('cod', '') or None
            bod = request.POST.get('bod', '') or None
            tss = request.POST.get('tss', '') or None
            
            # Convert to float for non-None values
            ph = float(ph) if ph is not None else None
            flow = float(flow) if flow is not None else None
            cod = float(cod) if cod is not None else None
            bod = float(bod) if bod is not None else None
            tss = float(tss) if tss is not None else None
            
            # Calculate total_flow automatically
            latest_record = WaterQualityData.objects.filter(user=user).order_by('-timestamp').first()
            if latest_record and flow is not None:
                total_flow = latest_record.total_flow + flow
            elif flow is not None:
                total_flow = flow
            else:
                total_flow = 0
            
            # Create new record with non-null values
            new_data = WaterQualityData(
                user=user,
                ph=ph if ph is not None else 0,
                flow=flow if flow is not None else 0,
                total_flow=total_flow,
                cod=cod if cod is not None else 0,
                bod=bod if bod is not None else 0,
                tss=tss if tss is not None else 0
            )
            
            new_data.save()
            
            return JsonResponse({'success': True})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User not found'})
        except ValueError as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

