"""
API Registry - Central location for all API endpoints
This file provides a complete overview of all available API endpoints
"""

# API Base URL: /api/

API_ENDPOINTS = {
    # Authentication
    'auth': {
        'login': '/api/auth/login/',
        'logout': '/api/auth/logout/',
        'token': '/api/auth/token/',
    },
    
    # Properties
    'properties': {
        'list': '/api/properties/',
        'detail': '/api/properties/{id}/',
        'create': '/api/properties/',
        'update': '/api/properties/{id}/',
        'delete': '/api/properties/{id}/',
        'types': '/api/property-types/',
        'images': '/api/properties/{id}/images/',
        'documents': '/api/properties/{id}/documents/',
    },
    
    # Owners
    'owners': {
        'list': '/api/owners/',
        'detail': '/api/owners/{id}/',
        'create': '/api/owners/',
        'update': '/api/owners/{id}/',
        'delete': '/api/owners/{id}/',
        'properties': '/api/owners/{id}/properties/',
    },
    
    # Clients
    'clients': {
        'list': '/api/clients/',
        'detail': '/api/clients/{id}/',
        'create': '/api/clients/',
        'update': '/api/clients/{id}/',
        'delete': '/api/clients/{id}/',
        'contracts': '/api/clients/{id}/contracts/',
    },
    
    # Contracts
    'contracts': {
        'list': '/api/contracts/',
        'detail': '/api/contracts/{id}/',
        'create': '/api/contracts/',
        'update': '/api/contracts/{id}/',
        'delete': '/api/contracts/{id}/',
        'payments': '/api/contracts/{id}/payments/',
        'renewals': '/api/contracts/{id}/renewals/',
    },
    
    # Maintenance
    'maintenance': {
        'list': '/api/maintenance/',
        'detail': '/api/maintenance/{id}/',
        'create': '/api/maintenance/',
        'update': '/api/maintenance/{id}/',
        'delete': '/api/maintenance/{id}/',
        'categories': '/api/maintenance-categories/',
        'schedule': '/api/maintenance-schedule/',
    },
    
    # Reports
    'reports': {
        'properties': '/api/reports/properties/',
        'contracts': '/api/reports/contracts/',
        'maintenance': '/api/reports/maintenance/',
        'financial': '/api/reports/financial/',
        'export': '/api/reports/export/{type}/',
    },
    
    # Dashboard
    'dashboard': {
        'stats': '/api/dashboard/stats/',
        'charts': '/api/dashboard/charts/',
        'activities': '/api/dashboard/activities/',
    },
}

# API Permissions Map
API_PERMISSIONS = {
    'properties': ['view_property', 'add_property', 'change_property', 'delete_property'],
    'owners': ['view_owner', 'add_owner', 'change_owner', 'delete_owner'],
    'clients': ['view_client', 'add_client', 'change_client', 'delete_client'],
    'contracts': ['view_contract', 'add_contract', 'change_contract', 'delete_contract'],
    'maintenance': ['view_maintenancerequest', 'add_maintenancerequest', 'change_maintenancerequest', 'delete_maintenancerequest'],
}

# API Response Formats
API_RESPONSE_FORMAT = {
    'success': {
        'status': 'success',
        'data': {},
        'message': 'Operation completed successfully'
    },
    'error': {
        'status': 'error',
        'errors': [],
        'message': 'Operation failed'
    },
    'list': {
        'status': 'success',
        'data': {
            'count': 0,
            'next': None,
            'previous': None,
            'results': []
        }
    }
}

def get_endpoint(module, action):
    """
    Get API endpoint URL
    
    Usage:
        get_endpoint('properties', 'list')  # Returns: /api/properties/
        get_endpoint('properties', 'detail')  # Returns: /api/properties/{id}/
    """
    if module in API_ENDPOINTS and action in API_ENDPOINTS[module]:
        return API_ENDPOINTS[module][action]
    return None

def get_all_endpoints():
    """Get all API endpoints as a flat dictionary"""
    endpoints = {}
    for module, actions in API_ENDPOINTS.items():
        for action, url in actions.items():
            key = f"{module}_{action}"
            endpoints[key] = url
    return endpoints

def print_api_documentation():
    """Print formatted API documentation"""
    print("=" * 80)
    print("ORIGIN APP - API DOCUMENTATION")
    print("=" * 80)
    print("\nBase URL: /api/")
    print("\nAvailable Endpoints:\n")
    
    for module, actions in API_ENDPOINTS.items():
        print(f"\n{module.upper()}:")
        print("-" * 40)
        for action, url in actions.items():
            print(f"  {action:20} {url}")
    
    print("\n" + "=" * 80)
