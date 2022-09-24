from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("electronics", views.index, name="electronics"),
    path("collectibles", views.index, name="collectibles"),
    path("others", views.index, name="others"),
    path("all_listings", views.index, name="all_listings"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("view_listing/<int:pk>", views.view_listing, name="view_listing"),
    path("add_watchlist/<int:pk>", views.add_watchlist, name="add_watchlist"),
    path("remove_watchlist/<int:pk>", views.add_watchlist_watchlist, name="remove_watchlist"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("close_auction/<int:pk>", views.close_auction, name="close_auction"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
