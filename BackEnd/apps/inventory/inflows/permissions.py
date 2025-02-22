from rest_framework.permissions import BasePermission
import logging

logger = logging.getLogger(__name__)

class InflowBasePermission(BasePermission):
    """
    Base permission class for Inflow operations.
    Ensures user is authenticated and has access to the company.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        try:
            # Ensure user has an associated employee
            employeer = request.user.employeer
            return True
        except Exception as e:
            logger.warning(
                "User without employee profile tried to access inflow",
                extra={
                    'user_email': request.user.email,
                    'error': str(e)
                }
            )
            return False
    
    def has_object_permission(self, request, view, obj):
        # Ensure user's company matches object's company
        return obj.companie == request.user.employeer.companie


class CanApproveInflow(InflowBasePermission):
    """
    Permission class for approving inflows.
    Requires 'can_approve_inflow' permission.
    """
    
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
            
        has_perm = request.user.has_perm('inflows.can_approve_inflow')
        if not has_perm:
            logger.warning(
                "User attempted to approve inflow without permission",
                extra={'user_email': request.user.email}
            )
        return has_perm


class CanRejectInflow(InflowBasePermission):
    """
    Permission class for rejecting inflows.
    Requires 'can_reject_inflow' permission.
    """
    
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
            
        has_perm = request.user.has_perm('inflows.can_reject_inflow')
        if not has_perm:
            logger.warning(
                "User attempted to reject inflow without permission",
                extra={'user_id': request.user.id}
            )
        return has_perm


class CanGenerateInflowReports(InflowBasePermission):
    """
    Permission class for generating inflow reports.
    Requires 'can_generate_inflow_reports' permission.
    """
    
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
            
        has_perm = request.user.has_perm('inflows.can_generate_inflow_reports')
        if not has_perm:
            logger.warning(
                "User attempted to generate inflow report without permission",
                extra={'user_id': request.user.id}
            )
        return has_perm


# Permission mapping for different user roles
INFLOW_PERMISSIONS = {
    'Owner': [
        'can_approve_inflow',
        'can_reject_inflow',
        'can_generate_inflow_reports'
    ],
    'CEO': [
        'can_approve_inflow',
        'can_reject_inflow',
        'can_generate_inflow_reports'
    ],
    'Admin': [
        'can_approve_inflow',
        'can_reject_inflow',
        'can_generate_inflow_reports'
    ],
    'Manager': [
        'can_approve_inflow',
        'can_reject_inflow'
    ],
    'Stock_Controller': []
}
