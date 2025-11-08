"""
URL configuration for Properties app
"""
from django.urls import path
from . import views

app_name = 'properties'

urlpatterns = [
    # Property CRUD
    path('', views.property_list, name='list'),
    path('dashboard/', views.property_dashboard, name='dashboard'),
    path('map/', views.property_map, name='map'),
    path('create/', views.property_create, name='create'),
    path('<int:pk>/', views.property_detail, name='detail'),
    path('<int:pk>/edit/', views.property_update, name='update'),
    path('<int:pk>/delete/', views.property_delete, name='delete'),
    
    # HTMX Partials
    path('partial/form/', views.property_form_partial, name='form_partial'),
    path('partial/form/<int:pk>/', views.property_form_partial, name='form_partial_edit'),
    path('partial/row/<int:pk>/', views.property_row_partial, name='row_partial'),
    
    # Property Images
    path('<int:property_pk>/images/upload/', views.property_image_upload, name='image_upload'),
    path('images/<int:pk>/delete/', views.property_image_delete, name='image_delete'),
    
    # Property Documents
    path('<int:property_pk>/documents/upload/', views.property_document_upload, name='document_upload'),
    path('documents/<int:pk>/delete/', views.property_document_delete, name='document_delete'),

    # Property Valuations
    path('<int:property_pk>/valuations/create/', views.property_valuation_create, name='valuation_create'),
    path('valuations/<int:pk>/delete/', views.property_valuation_delete, name='valuation_delete'),

    # Property Amenities
    path('<int:property_pk>/amenities/create/', views.property_amenity_create, name='amenity_create'),
    path('amenities/<int:pk>/delete/', views.property_amenity_delete, name='amenity_delete'),

    # Property Inspections
    path('<int:property_pk>/inspections/create/', views.property_inspection_create, name='inspection_create'),
    path('inspections/<int:pk>/delete/', views.property_inspection_delete, name='inspection_delete'),

    # Property Expenses
    path('<int:property_pk>/expenses/create/', views.property_expense_create, name='expense_create'),
    path('expenses/<int:pk>/delete/', views.property_expense_delete, name='expense_delete'),

    # Property Revenues
    path('<int:property_pk>/revenues/create/', views.property_revenue_create, name='revenue_create'),
    path('revenues/<int:pk>/delete/', views.property_revenue_delete, name='revenue_delete'),
    
    # Property Types
    path('types/', views.property_type_list, name='type_list'),
    path('types/create/', views.property_type_create, name='type_create'),
    path('types/<int:pk>/edit/', views.property_type_update, name='type_update'),
    path('types/<int:pk>/delete/', views.property_type_delete, name='type_delete'),
    
    # AJAX/API
    path('<int:pk>/toggle-status/', views.property_status_toggle, name='toggle_status'),
]
