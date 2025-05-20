from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, JsonResponse
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import logout, get_user_model
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from io import BytesIO
from .models import WaterQualityData, CustomUser, Reading, Machine
from .serializers import WaterQualityDataSerializer, ReadingSerializer
from .forms import CustomUserCreationForm
import logging
import requests
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from reportlab.lib import colors as reportlab_colors
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch

logger = logging.getLogger(__name__)
User = get_user_model()

def is_admin(user):
    return user.is_authenticated and user.is_admin

@login_required
def dashboard(request):
    if request.user.is_admin:
        total_users = CustomUser.objects.filter(role=CustomUser.USER).count()
        recent_data_count = (WaterQualityData.objects.filter(timestamp__gte=timezone.now() - timedelta(days=7)).count() +
                            Reading.objects.filter(recorded_at__gte=timezone.now() - timedelta(days=7)).count())
        active_machines = Machine.objects.count()
        recent_activities = []  # Implement activity log if needed
        return render(request, 'monitoring_app/admin_dashboard.html', {
            'total_users': total_users,
            'recent_data_count': recent_data_count,
            'active_machines': active_machines,
            'recent_activities': recent_activities
        })
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
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                password = f"{user.username}@123"
                user.set_password(password)
                user.save()
                messages.success(request, f'User {user.username} created successfully!')
                return redirect('user_management')
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
        if user != request.user:
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
def calibrate_flow(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        try:
            flow_number = int(request.POST.get('flow_number'))
            new_total = float(request.POST.get('new_total'))
            machine = Machine.objects.get(name=f'machine_flow_{flow_number}')
            latest_reading = Reading.objects.filter(
                user=user, 
                machine=machine, 
                parameter=f'flow{flow_number}'
            ).order_by('-recorded_at').first()
            if latest_reading:
                latest_reading.value = new_total
                latest_reading.save()
                messages.success(request, f'Total Flow {flow_number} calibrated successfully!')
            else:
                messages.error(request, "No flow data available to calibrate.")
            return redirect('user_management')
        except Machine.DoesNotExist:
            messages.error(request, f"Machine for Flow {flow_number} not found.")
        except ValueError as e:
            messages.error(request, f"Invalid input: {str(e)}")
        except Exception as e:
            messages.error(request, f"Error calibrating flow: {str(e)}")
    return render(request, 'monitoring_app/calibrate_flow.html', {'user': user})

@login_required
@user_passes_test(is_admin)
def fetch_external_flow(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    try:
        response = requests.get('https://api.example.com/flow_data')  # Replace with actual API
        data = response.json()
        for flow_number in [1, 2, 3]:
            if getattr(user, f'show_flow{flow_number}'):
                machine = Machine.objects.get(name=f'machine_flow_{flow_number}')
                flow_total = data.get(f'flow{flow_number}_total', 0)
                Reading.objects.create(
                    user=user,
                    machine=machine,
                    parameter=f'flow{flow_number}',
                    value=flow_total
                )
        messages.success(request, 'External flow data fetched and applied successfully!')
        return redirect('user_management')
    except Exception as e:
        messages.error(request, f"Error fetching external flow: {str(e)}")
        return redirect('user_management')

@login_required
@user_passes_test(is_admin)
def download_user_credentials(request, user_id):
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
        ['Password', f"{user.username}@123"],
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
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        user_id = self.request.query_params.get('user_id')
        if user_id:
            try:
                user = CustomUser.objects.get(id=user_id)
                context['show_ph'] = user.show_ph
                context['show_cod'] = user.show_cod
                context['show_bod'] = user.show_bod
                context['show_tss'] = user.show_tss
            except CustomUser.DoesNotExist:
                logger.error(f"User with ID {user_id} not found in get_serializer_context")
        return context
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            logger.error("Missing user_id parameter in water quality latest action")
            return Response({"error": "user_id parameter is required"}, status=400)
        try:
            latest_data = WaterQualityData.objects.filter(user_id=user_id).order_by('-timestamp').first()
            if latest_data:
                serializer = self.get_serializer(latest_data)
                return Response(serializer.data)
            else:
                logger.info(f"No water quality data found for user_id {user_id}")
                return Response({
                    'timestamp': None,
                    'ph': None,
                    'cod': None,
                    'bod': None,
                    'tss': None
                })
        except Exception as e:
            logger.error(f"Error in water quality latest action for user_id {user_id}: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=500)
    
    @action(detail=False, methods=['get'])
    def date_range(self, request):
        user_id = request.query_params.get('user_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        time_interval = request.query_params.get('time_interval', '0')
        
        if not all([user_id, start_date, end_date]):
            logger.error("Missing required parameters in water quality date_range action")
            return Response({"error": "user_id, start_date, and end_date parameters are required"}, status=400)
        
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            time_interval = int(time_interval)
        except ValueError:
            logger.error(f"Invalid date format or time_interval in water quality date_range: start_date={start_date}, end_date={end_date}, time_interval={time_interval}")
            return Response({"error": "Invalid date format. Use YYYY-MM-DD"}, status=400)
        
        if (end_date - start_date).days > 31:
            logger.error(f"Date range exceeds 31 days in water quality date_range: start_date={start_date}, end_date={end_date}")
            return Response({"error": "Date range cannot exceed 31 days"}, status=400)
        
        queryset = WaterQualityData.objects.filter(
            user_id=user_id,
            timestamp__date__gte=start_date,
            timestamp__date__lte=end_date
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
        logger.info(f"Returning {len(serializer.data)} water quality records for user_id {user_id}")
        return Response(serializer.data)

class ReadingViewSet(viewsets.ModelViewSet):
    queryset = Reading.objects.all()
    serializer_class = ReadingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def get_queryset(self):
        queryset = Reading.objects.all()
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        limit = self.request.query_params.get('limit')
        if limit and limit.isdigit():
            queryset = queryset.order_by('-recorded_at')[:int(limit)]
        else:
            queryset = queryset.order_by('-recorded_at')
        return queryset
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            logger.error("Missing user_id parameter in readings latest action")
            return Response({"error": "user_id parameter is required"}, status=400)
        latest_readings = {'flow1': None, 'flow2': None, 'flow3': None}
        try:
            for param in ['flow1', 'flow2', 'flow3']:
                reading = Reading.objects.filter(user_id=user_id, parameter=param).order_by('-recorded_at').first()
                if reading:
                    latest_readings[param] = {
                        'value': reading.value,
                        'recorded_at': reading.recorded_at.isoformat()
                    }
            logger.info(f"Returning latest readings for user_id {user_id}")
            return Response(latest_readings)
        except Exception as e:
            logger.error(f"Error in readings latest action for user_id {user_id}: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=500)
    
    @action(detail=False, methods=['get'])
    def date_range(self, request):
        user_id = request.query_params.get('user_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        time_interval = request.query_params.get('time_interval', '0')
        
        if not all([user_id, start_date, end_date]):
            logger.error("Missing required parameters in readings date_range action")
            return Response({"error": "user_id, start_date, and end_date parameters are required"}, status=400)
        
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            time_interval = int(time_interval)
        except ValueError:
            logger.error(f"Invalid date format or time_interval in readings date_range: start_date={start_date}, end_date={end_date}, time_interval={time_interval}")
            return Response({"error": "Invalid date format. Use YYYY-MM-DD"}, status=400)
        
        if (end_date - start_date).days > 31:
            logger.error(f"Date range exceeds 31 days in readings date_range: start_date={start_date}, end_date={end_date}")
            return Response({"error": "Date range cannot exceed 31 days"}, status=400)
        
        queryset = Reading.objects.filter(
            user_id=user_id,
            recorded_at__date__gte=start_date,
            recorded_at__date__lte=end_date
        ).order_by('recorded_at')
        
        if time_interval > 0:
            interval_seconds = time_interval * 60
            filtered_data = []
            last_timestamp = None
            data_list = list(queryset)
            for item in data_list:
                if last_timestamp is None:
                    filtered_data.append(item)
                    last_timestamp = item.recorded_at
                else:
                    time_diff = (item.recorded_at - last_timestamp).total_seconds()
                    if time_diff >= interval_seconds:
                        filtered_data.append(item)
                        last_timestamp = item.recorded_at
            queryset = filtered_data
        
        serializer = self.get_serializer(queryset, many=True)
        logger.info(f"Returning {len(serializer.data)} reading records for user_id {user_id}")
        return Response(serializer.data)

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
    latest_wq_data = WaterQualityData.objects.filter(user=user).order_by('-timestamp').first()
    latest_flow_readings = {
        'flow1': Reading.objects.filter(user=user, parameter='flow1').order_by('-recorded_at').first(),
        'flow2': Reading.objects.filter(user=user, parameter='flow2').order_by('-recorded_at').first(),
        'flow3': Reading.objects.filter(user=user, parameter='flow3').order_by('-recorded_at').first(),
    }
    all_wq_data = WaterQualityData.objects.filter(user=user).order_by('-timestamp')[:50]
    all_flow_readings = Reading.objects.filter(user=user).order_by('-recorded_at')[:50]
    return render(request, 'monitoring_app/live_status.html', {
        'user': user,
        'latest_wq_data': latest_wq_data,
        'latest_flow_readings': latest_flow_readings,
        'all_wq_data': all_wq_data,
        'all_flow_readings': all_flow_readings
    })

@login_required
def download_page(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, 'monitoring_app/download.html', {'user': user})

@login_required
def add_data(request):
    users = User.objects.all()
    machines = Machine.objects.all()
    return render(request, 'monitoring_app/add_data.html', {'users': users, 'machines': machines})

@login_required
def data_entry(request):
    if request.user.is_admin:
        users = User.objects.all()
        machines = Machine.objects.all()
        return render(request, 'monitoring_app/data_entry.html', {'users': users, 'machines': machines})
    return redirect('dashboard')

@login_required
def submit_data(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        try:
            user = User.objects.get(id=user_id)
            # Non-flow parameters
            ph = request.POST.get('ph', '') or None
            cod = request.POST.get('cod', '') or None
            bod = request.POST.get('bod', '') or None
            tss = request.POST.get('tss', '') or None
            ph = float(ph) if ph else None
            cod = float(cod) if cod else None
            bod = float(bod) if bod else None
            tss = float(tss) if tss else None
            # Save non-flow data
            if any([ph, cod, bod, tss]):
                new_wq_data = WaterQualityData(
                    user=user,
                    ph=ph,
                    cod=cod,
                    bod=bod,
                    tss=tss
                )
                new_wq_data.save()
            # Flow parameters
            for flow_number in [1, 2, 3]:
                flow_value = request.POST.get(f'flow{flow_number}', '') or None
                if flow_value:
                    flow_value = float(flow_value)
                    machine = Machine.objects.get(name=f'machine_flow_{flow_number}')
                    Reading.objects.create(
                        user=user,
                        machine=machine,
                        parameter=f'flow{flow_number}',
                        value=flow_value
                    )
            return JsonResponse({'success': True})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User not found'})
        except Machine.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Machine not found'})
        except ValueError as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

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
            # Collect selected parameters
            fields = [field for field in ['ph', 'flow1', 'flow2', 'flow3', 'cod', 'bod', 'tss'] if request.POST.get(field)]
            if not fields:
                messages.error(request, "Please select at least one parameter")
                return redirect('download_page', user_id=user_id)
            # Fetch data
            wq_queryset = WaterQualityData.objects.filter(
                user=user,
                timestamp__date__gte=start_date,
                timestamp__date__lte=end_date
            ).order_by('timestamp')
            flow_queryset = Reading.objects.filter(
                user=user,
                parameter__in=['flow1', 'flow2', 'flow3'],
                recorded_at__date__gte=start_date,
                recorded_at__date__lte=end_date
            ).order_by('recorded_at')
            # Apply time interval filtering
            if time_interval > 0:
                interval_seconds = time_interval * 60
                filtered_wq = []
                filtered_flow = []
                last_wq_timestamp = last_flow_timestamp = None
                for item in wq_queryset:
                    if last_wq_timestamp is None or (item.timestamp - last_wq_timestamp).total_seconds() >= interval_seconds:
                        filtered_wq.append(item)
                        last_wq_timestamp = item.timestamp
                for item in flow_queryset:
                    if last_flow_timestamp is None or (item.recorded_at - last_flow_timestamp).total_seconds() >= interval_seconds:
                        filtered_flow.append(item)
                        last_flow_timestamp = item.recorded_at
                wq_data = filtered_wq
                flow_data = filtered_flow
            else:
                wq_data = list(wq_queryset)
                flow_data = list(flow_queryset)
            # Combine data for export
            combined_data = []
            for wq in wq_data:
                entry = {
                    'timestamp': wq.timestamp,
                    'date': wq.timestamp.date(),
                    'ph': wq.ph if 'ph' in fields else None,
                    'cod': wq.cod if 'cod' in fields else None,
                    'bod': wq.bod if 'bod' in fields else None,
                    'tss': wq.tss if 'tss' in fields else None,
                    'flow1': None,
                    'flow2': None,
                    'flow3': None
                }
                combined_data.append(entry)
            for flow in flow_data:
                entry = next((e for e in combined_data if abs((e['timestamp'] - flow.recorded_at).total_seconds()) < 1), None)
                if not entry:
                    entry = {
                        'timestamp': flow.recorded_at,
                        'date': flow.recorded_at.date(),
                        'ph': None,
                        'cod': None,
                        'bod': None,
                        'tss': None,
                        'flow1': None,
                        'flow2': None,
                        'flow3': None
                    }
                    combined_data.append(entry)
                entry[flow.parameter] = flow.value
            combined_data.sort(key=lambda x: x['timestamp'])
            # Export to Excel
            if file_format == 'excel':
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
                for row_num, item in enumerate(combined_data, 2):
                    row_color = row_fill if row_num % 2 == 0 else alt_row_fill
                    date_cell = ws.cell(row=row_num, column=1, value=item['date'].strftime('%Y-%m-%d'))
                    date_cell.alignment = centered_alignment
                    date_cell.border = border
                    date_cell.fill = row_color
                    localized_timestamp = timezone.localtime(item['timestamp'])
                    time_cell = ws.cell(row=row_num, column=2, value=localized_timestamp.strftime('%H:%M:%S'))
                    time_cell.alignment = centered_alignment
                    time_cell.border = border
                    time_cell.fill = row_color
                    time_cell.number_format = '@'
                    for col_num, field in enumerate(fields, 3):
                        value = item[field]
                        if value is None:
                            value = 0.0
                        value = round(value, 2)
                        cell = ws.cell(row=row_num, column=col_num, value=value)
                        cell.alignment = centered_alignment
                        cell.border = border
                        cell.fill = row_color
                        cell.number_format = '0.00'
                response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = f'attachment; filename="Datasheet_{start_date}_to_{end_date}.xlsx"'
                wb.save(response)
                return response
            # Export to PDF
            elif file_format == 'pdf':
                response = HttpResponse(content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="Datasheet_{start_date}_to_{end_date}.pdf"'
                buffer = BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=0.5*inch, leftMargin=0.5*inch, topMargin=0.75*inch, bottomMargin=0.75*inch)
                elements = []
                styles = getSampleStyleSheet()
                elements.append(Paragraph(f"Datasheet for {user.username}", styles['Title']))
                elements.append(Paragraph(f"Date Range: {start_date} to {end_date}", styles['Normal']))
                elements.append(Spacer(1, 0.25*inch))
                table_data = [['Date', 'Time'] + [field.upper() for field in fields]]
                for item in combined_data:
                    localized_timestamp = timezone.localtime(item['timestamp'])
                    row = [item['date'].strftime('%Y-%m-%d'), localized_timestamp.strftime('%H:%M:%S')]
                    for field in fields:
                        value = item[field]
                        if value is None:
                            value = 0.0
                        value = f"{value:.2f}"
                        row.append(value)
                    table_data.append(row)
                table = Table(table_data, repeatRows=1)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), HexColor('#0096FF')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), reportlab_colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), reportlab_colors.white),
                    ('GRID', (0, 0), (-1, -1), 1, reportlab_colors.black),
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
            logger.error(f"Error downloading data for user_id {user_id}: {str(e)}", exc_info=True)
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('download_page', user_id=user_id)
    return redirect('download_page', user_id=user_id)