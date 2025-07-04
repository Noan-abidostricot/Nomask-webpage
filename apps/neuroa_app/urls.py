from . import views
from django.urls import path

urlpatterns = [
    path('', views.home, name='home'),
    path('settings/', views.settings, name='settings'),
    path('profile/', views.profile, name='profile'),

    path('condition/', views.ConditionView.as_view(), name='condition'),
    path('get-csrf-token/', views.get_csrf_token, name='get_csrf_token'),
    path('sign-up/', views.SignUpCandidateView.as_view(), name='sign_up'),
    path('send-validation-mail/', views.send_validation_mail, name='send_validation_mail'),
    path('validate-email/<uuid:token>/', views.validate_email, name='validate_email'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('update-profile/', views.update_profile, name='update_profile'),
    path('upload-photo/', views.upload_photo, name='upload_photo'),
    path('delete-photo/', views.delete_photo, name='delete_photo'),
    path('get-experience-data/<int:experience_id>/', views.get_experience_data, name='get_experience_data'),
    path('get-attribute-data/<int:attribute_id>/', views.get_attribute_data, name='get_attribute_data'),
    path('update-experience/', views.update_experience, name='update_experience'),
    path('update-attribute/', views.update_attribute, name='update_attribute'),
    path('delete-experience/', views.delete_experience, name='delete_experience'),
    path('delete-attribute/', views.delete_attribute, name='delete_attribute'),

    path('job-offer/<int:id>/', views.job_offer, name='job_offer'),
    path('job-search/', views.job_search, name='job_search'),
    path('application-monitoring/', views.application_monitoring, name='application_monitoring'),

    path('toggle-favorite/<int:job_offer_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('submit-application/<int:job_offer_id>/', views.submit_application, name='submit_application'),

    # PAGE EN ATTENTE
    path('test/', views.test, name='test'),
    path('contact/', views.contact, name='contact'),
    path('qui-sommes-nous/', views.qui_sommes_nous, name='qui_sommes_nous'),
    path('error-404/', views.error_404, name='error_404'),
    path('suivi-des-candidatures/', views.suivi_des_candidatures, name='suivi_des_candidatures'),

    # PAGE EN ATTENTE RECRUTEUR
    path('accueil-recruteur/', views.home_page_recruteur, name='home_page_recruteur'),
    path('tarifs/', views.tarifs, name='tarifs'),
    path('prestation/', views.prestation, name='prestation'),
    path('prestation-detaillee/', views.prestation_detaillee, name='prestation_detaillee'),
    path('create-job/', views.create_job, name='create_job'),
    path('job-create-form/', views.job_create_form, name='job_create_form'),
    path('gerer-mes-job-dashboard/', views.gerer_mes_job_dashboard, name='gerer_mes_job_dashboard'),
    path('mes-favoris/', views.mes_favoris, name='mes_favoris'),
]

