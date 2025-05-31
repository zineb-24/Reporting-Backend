from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from datetime import datetime, timedelta
from API.serializers import UserSerializer, SalleSerializer
from API.models import Salle
from .models import Reglement
from django.db.models.functions import TruncMonth
from django.db.models import Sum, F
from decimal import Decimal
from django.utils.translation import gettext as _
from django.utils import translation
from rest_framework.decorators import api_view


# View for language switching
@api_view(['POST'])
def set_language(request):
    """
    Set the language for the current session
    """
    language = request.data.get('language', 'en')
    if language in ['en', 'fr']:
        translation.activate(language)
        request.session[translation.LANGUAGE_SESSION_KEY] = language
        return Response({
            'language': language,
            'message': _('Language changed successfully')
        })
    return Response({
        'error': _('Invalid language')
    }, status=status.HTTP_400_BAD_REQUEST)


# Get the Salles the user is linked to
class UserDashboardView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_admin:
            return Response({
                'error': _('Unauthorized access'),
                'redirect': 'api/admin-dashboard/'
            }, status=status.HTTP_403_FORBIDDEN)
            
        user_data = UserSerializer(request.user).data
        
        # Get the salles the user is linked to
        user_salles = Salle.objects.filter(user_Links__id_user=request.user)
        salles_data = SalleSerializer(user_salles, many=True).data
        
        return Response({
            'message': _('User Dashboard'),
            'user': user_data,
            'salles': salles_data
        })

# View to retrieve the value of the Stats Cards depending on the Salle and the date parameters
class UserDashboardStatsView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Check if user is not admin
        if request.user.is_admin:
            return Response({
                'error': _('Unauthorized access'),
                'redirect': 'api/admin-dashboard/'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get query parameters
        salle_id = request.query_params.get('salle_id')
        date_type = request.query_params.get('date_type', 'month')  # month, year, or custom
        date_str = request.query_params.get('date')  # Format: YYYY-MM-DD for day, YYYY-MM for month, YYYY for year
        
        # Validate salle access
        try:
            # Check if user has access to this salle
            salle = Salle.objects.get(
                id_salle=salle_id,
                user_Links__id_user=request.user
            )
        except Salle.DoesNotExist:
            return Response({
                'error': _('You do not have access to this gym')
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Parse the date
        try:
            if not date_str:
                # Default to current month if no date provided
                today = timezone.now().date()
                start_date = today.replace(day=1)
                if today.month == 12:
                    end_date = today.replace(year=today.year+1, month=1, day=1) - timedelta(days=1)
                else:
                    end_date = today.replace(month=today.month+1, day=1) - timedelta(days=1)
            elif date_type == 'month' and len(date_str) >= 7:
                # For month: YYYY-MM
                year, month = map(int, date_str.split('-')[:2])
                start_date = datetime(year, month, 1).date()
                if month == 12:
                    end_date = datetime(year+1, 1, 1).date() - timedelta(days=1)
                else:
                    end_date = datetime(year, month+1, 1).date() - timedelta(days=1)
            elif date_type == 'year' and len(date_str) >= 4:
                # For year: YYYY
                year = int(date_str.split('-')[0])
                start_date = datetime(year, 1, 1).date()
                end_date = datetime(year, 12, 31).date()
            else:
                # Custom date range or single date
                date_parts = date_str.split('to')
                if len(date_parts) == 2:
                    start_date = datetime.strptime(date_parts[0].strip(), '%Y-%m-%d').date()
                    end_date = datetime.strptime(date_parts[1].strip(), '%Y-%m-%d').date()
                else:
                    # Single date
                    selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    start_date = selected_date
                    end_date = selected_date
        except (ValueError, IndexError):
            return Response({
                'error': _('Invalid date format')
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get all Reglements related to this salle for the current and all past dates
        all_reglements = Reglement.objects.filter(id_salle=salle)
        period_reglements = all_reglements.filter(
            DATE_REGLEMENT__date__gte=start_date,
            DATE_REGLEMENT__date__lte=end_date
        )
        
        # Statistics calculations
        # 1. Number of reglements in the period
        reglements_count = period_reglements.count()
        
        # 2. Number of new clients in the period
        # Get all clients that appeared before the start date
        existing_clients_before = all_reglements.filter(
            DATE_REGLEMENT__date__lt=start_date
        ).values_list('CLIENT', flat=True).distinct()
        
        # Get all clients in the current period
        clients_in_period = period_reglements.values_list('CLIENT', flat=True).distinct()
        
        # New clients are those in the current period that weren't present before
        new_clients_count = len(set(clients_in_period) - set(existing_clients_before))
        
        # 3. Number of new subscriptions in the period
        # Get all contracts that appeared before the start date
        existing_contracts_before = all_reglements.filter(
            DATE_CONTRAT__date__lt=start_date
        ).values_list('CONTRAT', flat=True).distinct()
        
        # Get all contracts in the current period
        contracts_in_period = period_reglements.filter(
            DATE_CONTRAT__date__gte=start_date,
            DATE_CONTRAT__date__lte=end_date
        ).values_list('CONTRAT', flat=True).distinct()
        
        # New subscriptions are those in the current period that weren't present before
        new_subscriptions_count = len(set(contracts_in_period) - set(existing_contracts_before))
        
        # 4. Number of expired contracts in the period
        expired_contracts_count = all_reglements.filter(
            DATE_FIN__date__gte=start_date,
            DATE_FIN__date__lte=end_date
        ).values('CONTRAT').distinct().count()
        
        # 5. Number of clients still subscribed
        # Clients with contracts that haven't expired yet
        current_date = timezone.now().date()
        active_clients_count = all_reglements.filter(
            DATE_FIN__date__gt=current_date
        ).values('CLIENT').distinct().count()

        # Calculate total amount for the period
        total_amount = period_reglements.aggregate(
            total=Sum('MONTANT')
        )['total'] or 0
        
        return Response({
            'salle_name': salle.name,
            'period': {
                'start_date': start_date,
                'end_date': end_date,
                'date_type': date_type
            },
            'stats': {
                'total_amount': total_amount,
                'reglements_count': reglements_count,
                'new_clients_count': new_clients_count,
                'new_subscriptions_count': new_subscriptions_count,
                'expired_contracts_count': expired_contracts_count,
                'active_clients_count': active_clients_count,
            },
            # Translation keys for the frontend
            'labels': {
                'total_amount': _('Total Amount'),
                'reglements_count': _('Number of Settlements'),
                'new_clients_count': _('New Clients'),
                'new_subscriptions_count': _('New Subscriptions'),
                'expired_contracts_count': _('Expired Contracts'),
                'active_clients_count': _('Active Clients'),
            }
        })

# View for the Total Revenue Bar Chart
class UserDashboardRevenueView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Check if user is not admin
        if request.user.is_admin:
            return Response({
                'error': _('Unauthorized access'),
                'redirect': 'api/admin-dashboard/'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get query parameters
        salle_id = request.query_params.get('salle_id')
        date_type = request.query_params.get('date_type', 'day')
        date_str = request.query_params.get('date')
        
        # Validate salle access
        try:
            # Check if user has access to this salle
            salle = Salle.objects.get(
                id_salle=salle_id,
                user_Links__id_user=request.user
            )
        except Salle.DoesNotExist:
            return Response({
                'error': _('You do not have access to this gym')
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Parse the date
        try:
            if date_type == 'custom':
                # Parse date range
                date_parts = date_str.split('to')
                if len(date_parts) == 2:
                    start_date = datetime.strptime(date_parts[0].strip(), '%Y-%m-%d').date()
                    end_date = datetime.strptime(date_parts[1].strip(), '%Y-%m-%d').date()
                    
                    # Ensure end_date is not before start_date
                    if end_date < start_date:
                        # Swap dates if needed
                        start_date, end_date = end_date, start_date
                    
                    # Limit range to a maximum of 30 days
                    max_days = 30
                    if (end_date - start_date).days > max_days:
                        end_date = start_date + timedelta(days=max_days - 1)  # -1 to include start date
                        
                else:
                    # Default to current month if parsing fails
                    today = timezone.now().date()
                    start_date = today.replace(day=1)
                    next_month = today.month + 1 if today.month < 12 else 1
                    next_year = today.year + 1 if today.month == 12 else today.year
                    end_date = today.replace(year=next_year, month=next_month, day=1) - timedelta(days=1)
                
                # Always group by day and show each day individually
                days_diff = (end_date - start_date).days
                revenue_data = []
                
                for i in range(days_diff + 1):  # +1 to include the end date
                    current_date = start_date + timedelta(days=i)
                    
                    daily_sum = Reglement.objects.filter(
                        id_salle=salle,
                        DATE_REGLEMENT__date=current_date
                    ).aggregate(total=Sum('MONTANT'))['total'] or 0
                    
                    # Format date as DD/MM for display
                    date_label = current_date.strftime('%d/%m')
                    
                    revenue_data.append({
                        'date': current_date.strftime('%Y-%m-%d'),
                        'amount': daily_sum,
                        'label': date_label
                    })
                    
            # Handle single day case
            elif date_type == 'day':
                # If single day selected, show the surrounding week
                if not date_str:
                    end_date = timezone.now().date()
                else:
                    end_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                
                start_date = end_date - timedelta(days=6)  # Show past 7 days
                
                # Group by day
                revenue_data = []
                for i in range(7):
                    current_date = start_date + timedelta(days=i)
                    daily_sum = Reglement.objects.filter(
                        id_salle=salle,
                        DATE_REGLEMENT__date=current_date
                    ).aggregate(total=Sum('MONTANT'))['total'] or 0
                    
                    # Format date as DD/MM for display
                    date_label = current_date.strftime('%d/%m')
                    
                    revenue_data.append({
                        'date': current_date.strftime('%Y-%m-%d'),
                        'amount': daily_sum,
                        'label': date_label
                    })
            
            elif date_type == 'month':
                # Handle month view - show each day of the month
                if not date_str:
                    today = timezone.now().date()
                    year, month = today.year, today.month
                else:
                    year, month = map(int, date_str.split('-')[:2])
                
                start_date = datetime(year, month, 1).date()
                if month == 12:
                    end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
                else:
                    end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)
                
                days_in_month = (end_date - start_date).days + 1
                revenue_data = []
                
                for i in range(days_in_month):
                    current_date = start_date + timedelta(days=i)
                    daily_sum = Reglement.objects.filter(
                        id_salle=salle,
                        DATE_REGLEMENT__date=current_date
                    ).aggregate(total=Sum('MONTANT'))['total'] or 0
                    
                    date_label = current_date.strftime('%d/%m')
                    
                    revenue_data.append({
                        'date': current_date.strftime('%Y-%m-%d'),
                        'amount': daily_sum,
                        'label': date_label
                    })
            
            elif date_type == 'year':
                # Handle year view - show each month of the year
                if not date_str:
                    year = timezone.now().date().year
                else:
                    year = int(date_str)
                
                revenue_data = []
                
                for month in range(1, 13):
                    month_start = datetime(year, month, 1).date()
                    if month == 12:
                        month_end = datetime(year + 1, 1, 1).date() - timedelta(days=1)
                    else:
                        month_end = datetime(year, month + 1, 1).date() - timedelta(days=1)
                    
                    monthly_sum = Reglement.objects.filter(
                        id_salle=salle,
                        DATE_REGLEMENT__date__gte=month_start,
                        DATE_REGLEMENT__date__lte=month_end
                    ).aggregate(total=Sum('MONTANT'))['total'] or 0
                    
                    month_label = datetime(year, month, 1).strftime('%b')
                    
                    revenue_data.append({
                        'date': month_start.strftime('%Y-%m-%d'),
                        'amount': monthly_sum,
                        'label': month_label
                    })
                
                start_date = datetime(year, 1, 1).date()
                end_date = datetime(year, 12, 31).date()
            
            else:
                # Handle other date types (default to showing current month by days)
                today = timezone.now().date()
                start_date = today.replace(day=1)
                if today.month == 12:
                    end_date = today.replace(year=today.year+1, month=1, day=1) - timedelta(days=1)
                else:
                    end_date = today.replace(month=today.month+1, day=1) - timedelta(days=1)
                
                # Group by day
                days_in_month = (end_date - start_date).days + 1
                revenue_data = []
                
                for i in range(days_in_month):
                    current_date = start_date + timedelta(days=i)
                    daily_sum = Reglement.objects.filter(
                        id_salle=salle,
                        DATE_REGLEMENT__date=current_date
                    ).aggregate(total=Sum('MONTANT'))['total'] or 0
                    
                    date_label = current_date.strftime('%d/%m')
                    
                    revenue_data.append({
                        'date': current_date.strftime('%Y-%m-%d'),
                        'amount': daily_sum,
                        'label': date_label
                    })
                
        except (ValueError, IndexError) as e:
            # Error handling
            return Response({
                'error': _('Invalid date format: %(error)s') % {'error': str(e)}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'revenue_data': revenue_data,
            'period': {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'date_type': date_type
            }
        })


# View for the Total Revenue Pie Chart
class UserDashboardDistributionView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Check if user is not admin
        if request.user.is_admin:
            return Response({
                'error': _('Unauthorized access'),
                'redirect': 'api/admin-dashboard/'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get query parameters
        salle_id = request.query_params.get('salle_id')
        category = request.query_params.get('category', 'payment_method')  # payment_method, subscription, agent
        date_type = request.query_params.get('date_type', 'month')
        date_str = request.query_params.get('date')
        
        # Validate salle access
        try:
            salle = Salle.objects.get(
                id_salle=salle_id,
                user_Links__id_user=request.user
            )
        except Salle.DoesNotExist:
            return Response({
                'error': _('You do not have access to this gym')
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Parse date range
        try:
            if not date_str:
                # Default to current month if no date provided
                today = timezone.now().date()
                start_date = today.replace(day=1)
                if today.month == 12:
                    end_date = today.replace(year=today.year+1, month=1, day=1) - timedelta(days=1)
                else:
                    end_date = today.replace(month=today.month+1, day=1) - timedelta(days=1)
            elif date_type == 'day':
                # For single day
                selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                start_date = selected_date
                end_date = selected_date
            elif date_type == 'custom':
                # Parse date range
                date_parts = date_str.split('to')
                if len(date_parts) == 2:
                    start_date = datetime.strptime(date_parts[0].strip(), '%Y-%m-%d').date()
                    end_date = datetime.strptime(date_parts[1].strip(), '%Y-%m-%d').date()
                    
                    # Ensure end_date is not before start_date
                    if end_date < start_date:
                        # Swap dates if needed
                        start_date, end_date = end_date, start_date
                else:
                    # Default to current month if parsing fails
                    today = timezone.now().date()
                    start_date = today.replace(day=1)
                    if today.month == 12:
                        end_date = today.replace(year=today.year+1, month=1, day=1) - timedelta(days=1)
                    else:
                        end_date = today.replace(month=today.month+1, day=1) - timedelta(days=1)
            elif date_type == 'month':
                # Handle month view
                if len(date_str) >= 7:
                    year, month = map(int, date_str.split('-')[:2])
                    start_date = datetime(year, month, 1).date()
                    if month == 12:
                        end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
                    else:
                        end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)
                else:
                    # Default to current month
                    today = timezone.now().date()
                    start_date = today.replace(day=1)
                    if today.month == 12:
                        end_date = today.replace(year=today.year+1, month=1, day=1) - timedelta(days=1)
                    else:
                        end_date = today.replace(month=today.month+1, day=1) - timedelta(days=1)
            elif date_type == 'year':
                # Handle year view
                if len(date_str) >= 4:
                    year = int(date_str)
                    start_date = datetime(year, 1, 1).date()
                    end_date = datetime(year, 12, 31).date()
                else:
                    # Default to current year
                    today = timezone.now().date()
                    start_date = datetime(today.year, 1, 1).date()
                    end_date = datetime(today.year, 12, 31).date()
            else:
                # Handle other date types (default to current month)
                today = timezone.now().date()
                start_date = today.replace(day=1)
                if today.month == 12:
                    end_date = today.replace(year=today.year+1, month=1, day=1) - timedelta(days=1)
                else:
                    end_date = today.replace(month=today.month+1, day=1) - timedelta(days=1)
            
            # Filter reglements based on date range
            reglements = Reglement.objects.filter(
                id_salle=salle,
                DATE_REGLEMENT__date__gte=start_date,
                DATE_REGLEMENT__date__lte=end_date
            )
            
            # Group by selected category
            if category == 'payment_method':
                # Group by MODE (payment method)
                distribution_data = reglements.values('MODE') \
                    .annotate(total=Sum('MONTANT')) \
                    .order_by('-total')
                
                # Convert to response format
                result = [
                    {
                        'name': item['MODE'] or str(_('Unknown')),
                        'value': float(item['total']) if item['total'] else 0
                    }
                    for item in distribution_data if item['MODE']
                ]
                
                # Add "Unknown" category for entries with null MODE
                unknown_total = reglements.filter(MODE__isnull=True).aggregate(total=Sum('MONTANT'))['total'] or 0
                if unknown_total > 0:
                    result.append({
                        'name': str(_('Unknown')),
                        'value': float(unknown_total)
                    })
                
            elif category == 'subscription':
                # Group by SOUSFAMILLE only
                distribution_data = reglements.values('SOUSFAMILLE') \
                    .annotate(total=Sum('MONTANT')) \
                    .order_by('-total')
                
                # Convert to response format with FAMILLE details
                result = []
                for item in distribution_data:
                    if item['SOUSFAMILLE']:
                        sousfamille_name = item['SOUSFAMILLE']
                        sousfamille_total = float(item['total']) if item['total'] else 0
                        
                        # Get all FAMILLE details for this SOUSFAMILLE
                        famille_details = reglements.filter(SOUSFAMILLE=item['SOUSFAMILLE']) \
                            .values('FAMILLE') \
                            .annotate(total=Sum('MONTANT')) \
                            .order_by('-total')
                        
                        # Format FAMILLE details
                        details = []
                        for detail in famille_details:
                            if detail['FAMILLE']:  # Only include non-null FAMILLE
                                details.append({
                                    'name': detail['FAMILLE'],
                                    'value': float(detail['total']) if detail['total'] else 0
                                })
                        
                        result.append({
                            'name': sousfamille_name,
                            'value': sousfamille_total,
                            'details': details if details else None  # Only add details if there are any
                        })
                
                # Add "Unknown" category for entries with null SOUSFAMILLE
                unknown_total = reglements.filter(SOUSFAMILLE__isnull=True).aggregate(total=Sum('MONTANT'))['total'] or 0
                if unknown_total > 0:
                    # Get FAMILLE details for unknown SOUSFAMILLE
                    unknown_famille = reglements.filter(SOUSFAMILLE__isnull=True) \
                        .values('FAMILLE') \
                        .annotate(total=Sum('MONTANT')) \
                        .order_by('-total')
                    
                    unknown_details = []
                    for detail in unknown_famille:
                        if detail['FAMILLE']:
                            unknown_details.append({
                                'name': detail['FAMILLE'],
                                'value': float(detail['total']) if detail['total'] else 0
                            })
                    
                    result.append({
                        'name': str(_('Unknown')),
                        'value': float(unknown_total),
                        'details': unknown_details if unknown_details else None
                    })
                
            elif category == 'agent':
                # Group by USERC (agent)
                distribution_data = reglements.values('USERC') \
                    .annotate(total=Sum('MONTANT')) \
                    .order_by('-total')
                
                # Convert to response format
                result = [
                    {
                        'name': item['USERC'] or str(_('Unknown')),
                        'value': float(item['total']) if item['total'] else 0
                    }
                    for item in distribution_data if item['USERC']
                ]
                
                # Add "Unknown" category for entries with null USERC
                unknown_total = reglements.filter(USERC__isnull=True).aggregate(total=Sum('MONTANT'))['total'] or 0
                if unknown_total > 0:
                    result.append({
                        'name': str(_('Unknown')),
                        'value': float(unknown_total)
                    })
            
            else:
                return Response({
                    'error': _('Invalid category type')
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Calculate total
            total_amount = reglements.aggregate(total=Sum('MONTANT'))['total'] or Decimal('0')
            
            # Sort results by value (highest first)
            result.sort(key=lambda x: x['value'], reverse=True)
            
            # Limit to top 5 categories for better visualization
            if len(result) > 6:
                # Keep top 4 and group the rest as "Others"
                top_items = result[:5]
                others_items = result[5:] 
                others_value = sum(item['value'] for item in others_items)
                
                if others_value > 0:
                    # Collect all details from others_items if they exist
                    others_details = []
                    for item in others_items:
                        if item.get('details'):
                            # If item has details (like SOUSFAMILLE with FAMILLE), add those details
                            others_details.extend(item['details'])
                        else:
                            # If item doesn't have details, add the item itself as a detail
                            others_details.append({
                                'name': item['name'],
                                'value': item['value']
                            })
                    
                    top_items.append({
                        'name': str(_('Others')),
                        'value': others_value,
                        'details': others_details if others_details else others_items  # Include the detail items
                    })
                result = top_items
            
            return Response({
                'distribution_data': result,
                'total': float(total_amount),
                'category': category,
                'period': {
                    'start_date': start_date.strftime('%Y-%m-%d'),
                    'end_date': end_date.strftime('%Y-%m-%d')
                }
            })
            
        except Exception as e:
            return Response({
                'error': _('Error processing request: %(error)s') % {'error': str(e)}
            }, status=status.HTTP_400_BAD_REQUEST)


# View for Reports - All Reglements Data
class UserDashboardReportsView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Check if user is not admin
        if request.user.is_admin:
            return Response({
                'error': _('Unauthorized access'),
                'redirect': 'api/admin-dashboard/'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get query parameters
        salle_id = request.query_params.get('salle_id')
        date_type = request.query_params.get('date_type', 'day')
        date_str = request.query_params.get('date')
        
        # Validate salle access
        try:
            salle = Salle.objects.get(
                id_salle=salle_id,
                user_Links__id_user=request.user
            )
        except Salle.DoesNotExist:
            return Response({
                'error': _('You do not have access to this gym')
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Parse date range (same logic as other views)
        try:
            if not date_str:
                today = timezone.now().date()
                start_date = today.replace(day=1)
                if today.month == 12:
                    end_date = today.replace(year=today.year+1, month=1, day=1) - timedelta(days=1)
                else:
                    end_date = today.replace(month=today.month+1, day=1) - timedelta(days=1)
            elif date_type == 'day':
                selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                start_date = selected_date
                end_date = selected_date
            elif date_type == 'custom':
                date_parts = date_str.split('to')
                if len(date_parts) == 2:
                    start_date = datetime.strptime(date_parts[0].strip(), '%Y-%m-%d').date()
                    end_date = datetime.strptime(date_parts[1].strip(), '%Y-%m-%d').date()
                    if end_date < start_date:
                        start_date, end_date = end_date, start_date
                else:
                    today = timezone.now().date()
                    start_date = today.replace(day=1)
                    if today.month == 12:
                        end_date = today.replace(year=today.year+1, month=1, day=1) - timedelta(days=1)
                    else:
                        end_date = today.replace(month=today.month+1, day=1) - timedelta(days=1)
            elif date_type == 'month':
                if len(date_str) >= 7:
                    year, month = map(int, date_str.split('-')[:2])
                    start_date = datetime(year, month, 1).date()
                    if month == 12:
                        end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
                    else:
                        end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)
                else:
                    today = timezone.now().date()
                    start_date = today.replace(day=1)
                    if today.month == 12:
                        end_date = today.replace(year=today.year+1, month=1, day=1) - timedelta(days=1)
                    else:
                        end_date = today.replace(month=today.month+1, day=1) - timedelta(days=1)
            elif date_type == 'year':
                if len(date_str) >= 4:
                    year = int(date_str)
                    start_date = datetime(year, 1, 1).date()
                    end_date = datetime(year, 12, 31).date()
                else:
                    today = timezone.now().date()
                    start_date = datetime(today.year, 1, 1).date()
                    end_date = datetime(today.year, 12, 31).date()
            else:
                today = timezone.now().date()
                start_date = today.replace(day=1)
                if today.month == 12:
                    end_date = today.replace(year=today.year+1, month=1, day=1) - timedelta(days=1)
                else:
                    end_date = today.replace(month=today.month+1, day=1) - timedelta(days=1)
            
            # Get all reglements for the date range
            reglements = Reglement.objects.filter(
                id_salle=salle,
                DATE_REGLEMENT__date__gte=start_date,
                DATE_REGLEMENT__date__lte=end_date
            ).order_by('-DATE_REGLEMENT')
            
            # Serialize the data
            reglements_data = []
            for reglement in reglements:
                reglements_data.append({
                    'ID_reglement': reglement.ID_reglement,
                    'CONTRAT': reglement.CONTRAT,
                    'CLIENT': reglement.CLIENT,
                    'DATE_CONTRAT': reglement.DATE_CONTRAT.isoformat() if reglement.DATE_CONTRAT else None,
                    'DATE_DEBUT': reglement.DATE_DEBUT.isoformat() if reglement.DATE_DEBUT else None,
                    'DATE_FIN': reglement.DATE_FIN.isoformat() if reglement.DATE_FIN else None,
                    'USERC': reglement.USERC,
                    'FAMILLE': reglement.FAMILLE,
                    'SOUSFAMILLE': reglement.SOUSFAMILLE,
                    'LIBELLE': reglement.LIBELLE,
                    'DATE_ASSURANCE': reglement.DATE_ASSURANCE.isoformat() if reglement.DATE_ASSURANCE else None,
                    'MONTANT': float(reglement.MONTANT),
                    'MODE': reglement.MODE,
                    'TARIFAIRE': reglement.TARIFAIRE,
                    'DATE_REGLEMENT': reglement.DATE_REGLEMENT.isoformat() if reglement.DATE_REGLEMENT else None,
                    'id_salle': reglement.id_salle.id_salle if reglement.id_salle else None,
                })
            
            return Response({
                'reglements': reglements_data,
                'period': {
                    'start_date': start_date.strftime('%Y-%m-%d'),
                    'end_date': end_date.strftime('%Y-%m-%d'),
                    'date_type': date_type
                },
                'total_count': len(reglements_data)
            })
            
        except Exception as e:
            return Response({
                'error': _('Error processing request: %(error)s') % {'error': str(e)}
            }, status=status.HTTP_400_BAD_REQUEST)
