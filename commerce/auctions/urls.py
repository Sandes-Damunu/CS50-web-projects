from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create/", views.CreateAuction, name="create_auction"),
    path("listing/<int:auction_id>/", views.listings_details, name="listing_details"),
    path("listing/<int:auction_id>/detail/", views.listings_details, name="auction_detail"),
    path("watchlist/", views.watchlist, name="watchlist"),
    path("categories/", views.categories, name="categories"),
    path("categories/<int:category_id>/", views.category_listings, name="category_listings"),
    path("listing/<int:auction_id>/bid/", views.place_bid, name="place_bid"),
    path("listing/<int:auction_id>/close/", views.close_auction, name="close_auction"),
   
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)