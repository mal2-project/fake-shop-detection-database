from django.conf.urls import re_path
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

from mal2_db import views


app_name = "mal2_db"

################################################################################
# URLS

urlpatterns = [

    # Base

    re_path(r"^websites/$", RedirectView.as_view(pattern_name="mal2_db:check_websites", permanent=False), name="websites"),
    re_path(r"^websites/all/$", views.AllWebsitesDataTableView.as_view(), name="all_websites"),
    re_path(r"^websites/all/data/$", views.AllWebsitesDataTableDataView.as_view(), name="all_websites_data"),
    re_path(r"^websites/to_check/$", views.WebsitesToCheckDataTableView.as_view(), name="check_websites"),
    re_path(r"^websites/to_check/data/$", views.WebsitesToCheckDataTableDataView.as_view(), name="check_websites_data"),
    re_path(r"^websites/disagreement/$", views.WebsitesDisagreementDataTableView.as_view(), name="disagreement_websites"),
    re_path(r"^websites/disagreement/data/$", views.WebsitesDisagreementDataTableDataView.as_view(), name="disagreement_websites_data"),
    re_path(r"^websites/disagreement/(?P<id>\d+)/edit/$", views.EditDisagreementWebsiteView.as_view(), name="edit_disagreement_website"),
    re_path(r"^websites/add/$", views.AddWebsiteView.as_view(), name="add_website"),
    re_path(r"^websites/(?P<id>\d+)/edit/$", views.EditWebsiteView.as_view(), name="edit_website"),
    re_path(r"^websites/(?P<id>\d+)/delete/$", views.DeleteWebsiteView.as_view(), name="delete_website"),
    re_path(r"^websites/(?P<id>\d+)/check/$", views.CheckWebsiteView.as_view(), name="check_website"),

    # re_path(r"^websites/no_verification_required/$", views.WebsitesNoVerificationRequiredDataTableView.as_view(), name="safe_websites"),
    # re_path(r"^websites/no_verification_required/data/$", views.WebsitesNoVerificationRequiredDataTableDataView.as_view(), name="safe_websites_data"),
    # re_path(r"^websites/unsure/$", views.WebsitesUnsureDataTableView.as_view(), name="unsure_websites"),
    # re_path(r"^websites/unsure/data/$", views.WebsitesUnsureDataTableDataView.as_view(), name="unsure_websites_data"),
    # re_path(r"^websites/no_fake/$", views.WebsitesNoFakeDataTableView.as_view(), name="no_fake_websites"),
    # re_path(r"^wesites/no_fake/data/$", views.WebsitesNoFakeDataTableDataView.as_view(), name="no_fake_websites_data"),
    # re_path(r"^websites/others/$", views.WebsitesOtherDataTableView.as_view(), name="other_websites"),
    # re_path(r"^wesites/others/data/$", views.WebsitesOtherDataTableDataView.as_view(), name="other_websites_data"),
    # re_path(r"^websites/online_shop/$", views.WebsitesOnlineShopsDataTableView.as_view(), name="online_shop"),
    # re_path(r"^wesites/online_shop/data/$", views.WebsitesOnlineShopsDataTableDataView.as_view(), name="online_shop_data"),

    re_path(r"^db/$", RedirectView.as_view(pattern_name="mal2_db:fake_shop", permanent=False), name="db"),
    re_path(r"^db/fake_shop/$", views.FakeShopDataTableView.as_view(), name="fake_shop"),
    re_path(r"^db/fake_shop/data/$", views.FakeShopDataTableDataView.as_view(), name="fake_shop_data"),
    re_path(r"^db/fake_shop/add$", views.AddFakeShopView.as_view(), name="add_fake_shop"),
    re_path(r"^db/fake_shop/(?P<website_id>\d+)/add$", views.AddFakeShopView.as_view(), name="add_fake_shop"),
    re_path(r"^db/fake_shop/(?P<id>\d+)/edit$", views.EditFakeShopView.as_view(), name="edit_fake_shop"),
    re_path(r"^db/fake_shop/(?P<id>\d+)/delete/$", views.DeleteFakeShopView.as_view(), name="delete_fake_shop"),
    re_path(r"^db/fake_shop/(?P<id>\d+)/details/$", views.FakeShopDetailsView.as_view(), name="fake_shop_details"),

    re_path(r"^db/counterfeiter/$", views.CounterfeitersDataTableView.as_view(), name="counterfeiters"),
    re_path(r"^db/counterfeiter/data/$", views.CounterfeitersDataTableDataView.as_view(), name="counterfeiters_data"),
    re_path(r"^db/counterfeiter/add/$", views.AddCounterfeiterView.as_view(), name="add_counterfeiter"),
    re_path(r"^db/counterfeiter/(?P<website_id>\d+)/add/$", views.AddCounterfeiterView.as_view(), name="add_counterfeiter"),
    re_path(r"^db/counterfeiter/(?P<id>\d+)/edit/$", views.EditCounterfeiterView.as_view(), name="edit_counterfeiter"),
    re_path(r"^db/counterfeiter/(?P<id>\d+)/delete/$", views.DeleteCounterfeiterView.as_view(), name="delete_counterfeiter"),
    re_path(r"^db/counterfeiter/(?P<id>\d+)/details/$", views.CounterfeiterDetailsView.as_view(), name="counterfeiter_details"),

    # Authentication

    re_path(r"^users/signin/$", views.SignInView.as_view(), name="signin"),
    re_path(r"^users/signout/$", auth_views.LogoutView.as_view(), name="signout"),
    re_path(r"^users/signup/$", views.SignUpView.as_view(), name="signup"),
    re_path(r"^users/signup/done/$", views.SignUpDoneView.as_view(), name="signup_done"),
    re_path(r"^users/email/verification/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$", views.EmailVerificationView.as_view(), name="email_verification"),
    re_path(r"^users/password/reset/$", views.PasswordResetView.as_view(), name="password_reset"),
    re_path(r"^users/password/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$", views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    re_path(r"^users/password/reset/done/$", views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    re_path(r"^users/password/set/$", auth_views.PasswordResetCompleteView.as_view(
        template_name="mal2_users/registration/password_reset_complete.html",
    ), name="password_reset_complete"),
    re_path(r"^users/password/change/$", views.PasswordChangeView.as_view(), name="password_change"),

    # Users

    re_path(r"^users/$", views.UsersDataTableView.as_view(), name="users_data_table"),
    re_path(r"^users/data/$", views.UsersDataTableDataView.as_view(), name="users_data_table_data"),
    re_path(r"^users/add/$", views.AddUserView.as_view(), name="add_user"),
    re_path(r"^users/(?P<pk>\d+)/delete/$", views.DeleteUserView.as_view(), name="delete_user"),
    re_path(r"^users/(?P<pk>\d+)/edit/$", views.EditUserView.as_view(), name="edit_user"),
    re_path(r"^users/(?P<pk>\d+)/set_password/", views.SetPasswordUserView.as_view(), name="set_user_password"),
]
