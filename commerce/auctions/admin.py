from django.contrib import admin
from .models import User, Auction, Bid, Comment, Category, Watchlist, Listing

# Register your models here.


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff',)
    search_fields = ('username', 'email')
admin.site.register(User, UserAdmin)

class AuctionAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'starting_price', 'current_price', 'is_active', 'winner', 'start_time', 'end_time')
    search_fields = ('title', 'owner__username')
    list_filter = ('is_active', 'category')
    readonly_fields = ('start_time', 'end_time')
admin.site.register(Auction, AuctionAdmin)

class BidAdmin(admin.ModelAdmin):
    list_display = ('auction', 'user', 'amount', 'timestamp')
    search_fields = ('auction__title', 'user__username')
    list_filter = ('auction', 'user')
    readonly_fields = ('timestamp',)
admin.site.register(Bid, BidAdmin)

class CommentAdmin(admin.ModelAdmin):
    list_display = ('auction', 'user', 'content', 'timestamp')
    search_fields = ('auction__title', 'user__username', 'content')
    list_filter = ('auction', 'user')
    readonly_fields = ('timestamp',)
admin.site.register(Comment, CommentAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
admin.site.register(Category, CategoryAdmin)

class WatchlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'auction',)
    search_fields = ('user__username', 'auction__title')
admin.site.register(Watchlist, WatchlistAdmin)

class ListingAdmin(admin.ModelAdmin):
    list_display = ('auction', 'category')
    search_fields = ('auction__title', 'category__name')
    list_filter = ('category',)
admin.site.register(Listing, ListingAdmin)