from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, JsonResponse
from datetime import datetime
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import logout
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from io import BytesIO
from .models import WaterQualityData, CustomUser
from .serializers import WaterQualityDataSerializer, UserSerializer
from .forms import CustomUserCreationForm
from django.contrib.auth import get_user_model
import logging

# Set up logging
logger = logging.getLogger(__name__)

User = get_user_model()

def is_admin(user):
    return user.is_authenticated and user.is_admin

@login_required
def dashboard(request):
    if request.user.is_admin:
        return render(request, 'monitoring_app/admin_dashboard.html')
    return render(request, 'monitoring_app/user_dashboard.html')

@login_required
def all_users_dashboard(request):
    if request.user.is_admin:
        users = CustomUser.objects.filter(role=CustomUser.USER)
        return render(request, 'monitoring_app/dashboard.html', {'users': users})
    return redirect('dashboard')

@login_required
@user_passes_test(is_admin)
def user_management(request):
    users = CustomUser.objects.all()
    return render(request, 'monitoring_app/user_management.html', {'users': users})

@login_required
@user_passes_test(is_admin)
def add_user(request):
    if request.method == 'POST':
        logger.debug(f"POST data: {request.POST}")
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                password = f"{user.username}@123"
                user.set_password(password)
                user.save()
                messages.success(request, f'User {user.username} created successfully!')
                return redirect('user_management')  # Ensure this redirects correctly
            except Exception as e:
                logger.error(f"Error saving user: {e}")
                messages.error(request, f"Error creating user: {str(e)}")
        else:
            logger.error(f"Form errors: {form.errors}")
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'monitoring_app/add_user.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def delete_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        if user != request.user:  # Prevent self-deletion
            user.delete()
            messages.success(request, f'User {user.username} deleted successfully!')
        else:
            messages.error(request, "You cannot delete your own account!")
        return redirect('user_management')
    return render(request, 'monitoring_app/delete_user_confirm.html', {'user': user})

@login_required
@user_passes_test(is_admin)
def edit_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'User {user.username} updated successfully!')
            return redirect('user_management')
        else:
            logger.error(f"Edit user form errors: {form.errors}")
    else:
        form = CustomUserCreationForm(instance=user)
    return render(request, 'monitoring_app/add_user.html', {'form': form, 'edit_mode': True})

@login_required
@user_passes_test(is_admin)
def download_user_credentials(request, user_id):
    """
    View for downloading user credentials as PDF.
    """
    user = get_object_or_404(CustomUser, id=user_id)
    return generate_user_pdf(user)

def generate_user_pdf(user):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    elements.append(Paragraph("New User Credentials", styles['Title']))
    elements.append(Spacer(1, 12))
    
    user_data = [
        ['Username', user.username],
        ['Password', f"{user.username}@123"],  # Default password format
        ['Email', user.email],
        ['Role', user.get_role_display()],
        ['First Name', user.first_name],
        ['Last Name', user.last_name],
        ['Contact Number', user.contact_number or '-'],
        ['Address', user.address or '-'],
        ['State', user.state or '-'],
        ['State Code', user.state_code or '-']
    ]
    
    table = Table(user_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(table)
    doc.build(elements)
    
    pdf = buffer.getvalue()
    buffer.close()
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="user_{user.username}_credentials.pdf"'
    response.write(pdf)
    return response

class WaterQualityDataViewSet(viewsets.ModelViewSet):
    queryset = WaterQualityData.objects.all()
    serializer_class = WaterQualityDataSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def get_queryset(self):
        queryset = WaterQualityData.objects.all()
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        limit = self.request.query_params.get('limit')
        if limit and limit.isdigit():
            queryset = queryset.order_by('-timestamp')[:int(limit)]
        else:
            queryset = queryset.order_by('-timestamp')
        return queryset
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
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
        user_id = request.query_params.get('user_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        time_interval = request.query_params.get('time_interval', '0')
        
        if not all([user_id, start_date, end_date]):
            return Response({"error": "user_id, start_date, and end_date parameters are required"}, status=400)
        
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            time_interval = int(time_interval)
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD"}, status=400)
        
        if (end_date - start_date).days > 31:
            return Response({"error": "Date range cannot exceed 31 days"}, status=400)
        
        queryset = WaterQualityData.objects.filter(
            user_id=user_id,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('timestamp')
        
        if time_interval > 0:
            interval_seconds = time_interval * 60
            filtered_data = []
            last_timestamp = None
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
            queryset = filtered_data
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

@login_required
def logout_confirm(request):
    if request.method == 'POST':
        if 'confirm' in request.POST:
            logout(request)
            return redirect('login')
        return redirect('dashboard')
    return render(request, 'monitoring_app/logout_confirm.html')

@login_required
def live_status(request, user_id):
    user = get_object_or_404(User, id=user_id)
    latest_data = WaterQualityData.objects.filter(user=user).order_by('-timestamp').first()
    all_data = WaterQualityData.objects.filter(user=user).order_by('-timestamp')[:50]
    return render(request, 'monitoring_app/live_status.html', {
        'user': user,
        'latest_data': latest_data,
        'all_data': all_data
    })

@login_required
def download_page(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, 'monitoring_app/download.html', {'user': user})

@login_required
def add_data(request):
    users = User.objects.all()
    return render(request, 'monitoring_app/add_data.html', {'users': users})

@login_required
def data_entry(request):
    if request.user.is_admin:
        users = User.objects.all()
        return render(request, 'monitoring_app/data_entry.html', {'users': users})
    return redirect('dashboard')

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
    data = list(queryset.values('id', 'user_id', 'timestamp', 'ph', 'flow', 'daily_flow', 'total_flow', 'cod', 'bod', 'tss', 'date'))
    # Convert data for JSON serialization and ensure daily_flow is present
    for item in data:
        if item['daily_flow'] is None:
            item['daily_flow'] = 0.0
        # Convert dates to ISO format string
        if 'timestamp' in item and item['timestamp']:
            item['timestamp'] = item['timestamp'].isoformat()
        if 'date' in item and item['date']:
            item['date'] = item['date'].isoformat()
    return JsonResponse(data, safe=False)

def custom_logout(request):
    logout(request)
    return redirect('login')

@login_required
def download_data(request, user_id):
    if request.method == 'POST':
        try:
            # Print POST data for debugging
            logger.debug(f"Download POST data: {request.POST}")
            
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
            
            if time_interval > 0:
                interval_seconds = time_interval * 60
                filtered_data = []
                last_timestamp = None
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
                data = filtered_data
            else:
                data = list(queryset)
            
            fields = [field for field in ['ph', 'flow', 'daily_flow', 'total_flow', 'cod', 'bod', 'tss'] if request.POST.get(field)]
            logger.debug(f"Selected fields: {fields}")
            
            if not fields:
                messages.error(request, "Please select at least one parameter")
                return redirect('download_page', user_id=user_id)
            
            if file_format == 'excel':
                import openpyxl
                from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
                
                wb = openpyxl.Workbook()
                ws = wb.active
                ws.title = "Water Quality Data"
                
                header_font = Font(bold=True, color="FFFFFF")
                header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
                centered_alignment = Alignment(horizontal="center", vertical="center")
                border = Border(left=Side(style="thin"), right=Side(style="thin"), top=Side(style="thin"), bottom=Side(style="thin"))
                
                header = ['Date', 'Time'] + [field.upper() for field in fields]
                for col_num, column_title in enumerate(header, 1):
                    cell = ws.cell(row=1, column=col_num, value=column_title)
                    cell.font = header_font
                    cell.fill = header_fill
                    cell.alignment = centered_alignment
                    cell.border = border
                    ws.column_dimensions[openpyxl.utils.get_column_letter(col_num)].width = max(12, len(column_title) + 4)
                
                row_fill = PatternFill(start_color="E9EDF4", end_color="E9EDF4", fill_type="solid")
                alt_row_fill = PatternFill(start_color="D3DFEE", end_color="D3DFEE", fill_type="solid")
                
                for row_num, item in enumerate(data, 2):
                    row_color = row_fill if row_num % 2 == 0 else alt_row_fill
                    date_cell = ws.cell(row=row_num, column=1, value=item.date.strftime('%Y-%m-%d'))
                    date_cell.alignment = centered_alignment
                    date_cell.border = border
                    date_cell.fill = row_color
                    
                    localized_timestamp = timezone.localtime(item.timestamp)
                    time_cell = ws.cell(row=row_num, column=2, value=localized_timestamp.strftime('%H:%M:%S'))
                    time_cell.alignment = centered_alignment
                    time_cell.border = border
                    time_cell.fill = row_color
                    time_cell.number_format = '@'
                    
                    for col_num, field in enumerate(fields, 3):
                        value = getattr(item, field)
                        if value is None:
                            value = 0.0  # Set default value if None
                        if field in ['daily_flow', 'total_flow', 'ph', 'flow', 'cod', 'bod', 'tss'] and value is not None:
                            value = round(value, 2)
                        cell = ws.cell(row=row_num, column=col_num, value=value)
                        cell.alignment = centered_alignment
                        cell.border = border
                        cell.fill = row_color
                        if field in ['daily_flow', 'total_flow', 'ph', 'flow', 'cod', 'bod', 'tss']:
                            cell.number_format = '0.00'
                
                response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = f'attachment; filename="water_quality_data_{start_date}_to_{end_date}.xlsx"'
                wb.save(response)
                return response
            
            elif file_format == 'pdf':
                from reportlab.lib import colors
                from reportlab.lib.colors import HexColor
                from reportlab.lib.units import inch
                
                response = HttpResponse(content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="water_quality_data_{start_date}_to_{end_date}.pdf"'
                
                buffer = BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=0.5*inch, leftMargin=0.5*inch, topMargin=0.75*inch, bottomMargin=0.75*inch)
                elements = []
                
                styles = getSampleStyleSheet()
                elements.append(Paragraph(f"Water Quality Data for {user.username}", styles['Title']))
                elements.append(Paragraph(f"Date Range: {start_date} to {end_date}", styles['Normal']))
                elements.append(Spacer(1, 0.25*inch))
                
                table_data = [['Date', 'Time'] + [field.upper() for field in fields]]
                for item in data:
                    localized_timestamp = timezone.localtime(item.timestamp)
                    row = [item.date.strftime('%Y-%m-%d'), localized_timestamp.strftime('%H:%M:%S')]
                    for field in fields:
                        value = getattr(item, field)
                        if value is None:
                            value = 0.0  # Set default value if None
                        if field in ['daily_flow', 'total_flow', 'ph', 'flow', 'cod', 'bod', 'tss'] and value is not None:
                            value = f"{value:.2f}"
                        else:
                            value = str(value)
                        row.append(value)
                    table_data.append(row)
                
                table = Table(table_data, repeatRows=1)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), HexColor('#0096FF')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                
                elements.append(table)
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
            logger.error(f"Error downloading data: {str(e)}")
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('download_page', user_id=user_id)
    
    return redirect('download_page', user_id=user_id)

@login_required
def submit_data(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        try:
            user = User.objects.get(id=user_id)
            ph = request.POST.get('ph', '') or None
            flow = request.POST.get('flow', '') or None
            cod = request.POST.get('cod', '') or None
            bod = request.POST.get('bod', '') or None
            tss = request.POST.get('tss', '') or None
            
            ph = float(ph) if ph else None
            flow = float(flow) if flow else None
            cod = float(cod) if cod else None
            bod = float(bod) if bod else None
            tss = float(tss) if tss else None
            
            latest_record = WaterQualityData.objects.filter(user=user).order_by('-timestamp').first()
            total_flow = (latest_record.total_flow + flow) if latest_record and flow else (flow or 0)
            
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