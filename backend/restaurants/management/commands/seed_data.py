"""Seed FoodFlow with Swiggy-style restaurants and menus.

Usage: python manage.py seed_data [--flush]
Idempotent: skips restaurants that already exist unless --flush is given.
Also creates a demo admin (admin@foodflow.app / admin123) and demo user
(demo@foodflow.app / demo1234) when missing.
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from restaurants.models import MenuCategory, MenuItem, Restaurant

User = get_user_model()

RESTAURANTS = [
    {
        'name': 'Biryani Blues',
        'cuisine': 'Biryani, North Indian, Mughlai',
        'rating': '4.4',
        'rating_count': 12400,
        'delivery_minutes': 32,
        'price_for_two': 400,
        'address': '12 Connaught Place, New Delhi',
        'promoted': True,
        'offer_text': '50% OFF up to ₹100',
        'emoji': '🍛',
        'gradient': 'linear-gradient(135deg, #f59e0b, #b45309)',
        'menu': {
            'Biryani': [
                ('Hyderabadi Chicken Dum Biryani', 'Slow-cooked basmati, tender chicken, saffron', 289, False, True, '🍗'),
                ('Mutton Biryani', 'Aged basmati rice with marinated mutton', 349, False, True, '🍖'),
                ('Veg Dum Biryani', 'Garden vegetables layered with fragrant rice', 219, True, False, '🥘'),
                ('Egg Biryani', 'Boiled eggs in masala rice', 199, False, False, '🍳'),
            ],
            'Sides': [
                ('Chicken 65', 'Spicy deep-fried chicken bites', 199, False, True, '🍗'),
                ('Raita', 'Cooling curd with cucumber', 49, True, False, '🥛'),
                ('Gulab Jamun (2 pcs)', 'Warm dumplings in sugar syrup', 79, True, False, '🍮'),
            ],
        },
    },
    {
        'name': 'Pizza Palace',
        'cuisine': 'Pizza, Italian, Fast Food',
        'rating': '4.2',
        'rating_count': 8900,
        'delivery_minutes': 25,
        'price_for_two': 350,
        'address': 'MG Road, Bengaluru',
        'promoted': True,
        'offer_text': 'Free delivery above ₹149',
        'emoji': '🍕',
        'gradient': 'linear-gradient(135deg, #f87171, #dc2626)',
        'menu': {
            'Pizzas': [
                ('Margherita Classic', 'Fresh mozzarella, basil, tomato sauce', 199, True, True, '🍕'),
                ('Farmhouse Veggie', 'Onion, capsicum, corn, mushroom', 279, True, True, '🍕'),
                ('Chicken Pepperoni', 'Double pepperoni with cheese burst', 349, False, True, '🍕'),
                ('Paneer Tikka Pizza', 'Tandoori paneer with mint drizzle', 299, True, False, '🧀'),
            ],
            'Garlic Breads & Sides': [
                ('Cheesy Garlic Bread', 'Stuffed with three cheeses', 129, True, True, '🥖'),
                ('BBQ Chicken Wings (6)', 'Smoky BBQ glazed wings', 189, False, False, '🍗'),
                ('Choco Lava Cake', 'Molten chocolate centre', 99, True, True, '🍫'),
            ],
        },
    },
    {
        'name': 'Dosa Corner',
        'cuisine': 'South Indian, Breakfast, Dosa',
        'rating': '4.6',
        'rating_count': 21500,
        'delivery_minutes': 20,
        'price_for_two': 200,
        'address': 'Jayanagar 4th Block, Bengaluru',
        'is_pure_veg': True,
        'offer_text': '20% OFF up to ₹50',
        'emoji': '🥞',
        'gradient': 'linear-gradient(135deg, #fbbf24, #f59e0b)',
        'menu': {
            'Dosas': [
                ('Masala Dosa', 'Crispy dosa, potato masala, sambar & chutney', 119, True, True, '🥞'),
                ('Ghee Roast Dosa', 'Roasted in pure ghee, golden crisp', 149, True, False, '🧈'),
                ('Paneer Dosa', 'Stuffed with spiced paneer', 169, True, False, '🧀'),
                ('Mysore Masala Dosa', 'Spicy red chutney spread', 139, True, False, '🌶️'),
            ],
            'Idli & Vada': [
                ('Idli (3 pcs)', 'Steamed rice cakes with sambar', 79, True, True, '⚪'),
                ('Medu Vada (2 pcs)', 'Crispy lentil doughnuts', 69, True, False, '🍩'),
                ('Filter Coffee', 'Traditional South Indian brew', 39, True, True, '☕'),
            ],
        },
    },
    {
        'name': 'Burger Barn',
        'cuisine': 'Burgers, American, Fast Food',
        'rating': '4.1',
        'rating_count': 5400,
        'delivery_minutes': 18,
        'price_for_two': 300,
        'address': 'Sector 29, Gurugram',
        'offer_text': 'Buy 1 Get 1 FREE',
        'emoji': '🍔',
        'gradient': 'linear-gradient(135deg, #fb923c, #ea580c)',
        'menu': {
            'Burgers': [
                ('Classic Veg Burger', 'Crispy patty, lettuce, house sauce', 89, True, True, '🍔'),
                ('Paneer Zinger Burger', 'Spicy crunchy paneer patty', 129, True, True, '🍔'),
                ('Chicken Maharaja Burger', 'Double chicken patty with cheese', 189, False, True, '🍔'),
                ('Double Cheese Burger', 'Twin beef-free patties, extra cheese', 159, False, False, '🍔'),
            ],
            'Fries & Shakes': [
                ('Peri Peri Fries', 'Seasoned crispy fries', 99, True, True, '🍟'),
                ('Oreo Milkshake', 'Thick shake with crushed Oreos', 149, True, False, '🥤'),
                ('Cold Coffee', 'Chilled frothy coffee', 99, True, False, '🧋'),
            ],
        },
    },
    {
        'name': 'Wok of China',
        'cuisine': 'Chinese, Noodles, Momos',
        'rating': '4.0',
        'rating_count': 4200,
        'delivery_minutes': 28,
        'price_for_two': 350,
        'address': 'Koramangala, Bengaluru',
        'offer_text': '₹125 OFF above ₹599',
        'emoji': '🍜',
        'gradient': 'linear-gradient(135deg, #ef4444, #7f1d1d)',
        'menu': {
            'Momos': [
                ('Steamed Veg Momos (6)', 'Delicate wrappers, veggie filling', 99, True, True, '🥟'),
                ('Fried Chicken Momos (6)', 'Crispy outside, juicy inside', 129, False, True, '🥟'),
                ('Tandoori Momos (6)', 'Charred with tandoori masala', 139, True, False, '🔥'),
            ],
            'Noodles & Rice': [
                ('Hakka Noodles Veg', 'Wok-tossed with crunchy veggies', 149, True, True, '🍜'),
                ('Chicken Chow Mein', 'Stir-fried noodles with chicken', 189, False, False, '🍜'),
                ('Burnt Garlic Fried Rice', 'Aromatic garlic rice', 169, True, False, '🍚'),
                ('Chilli Paneer Dry', 'Indo-Chinese paneer starter', 199, True, False, '🌶️'),
            ],
        },
    },
    {
        'name': 'Green Bowl Salads',
        'cuisine': 'Healthy Food, Salads, Continental',
        'rating': '4.3',
        'rating_count': 2100,
        'delivery_minutes': 22,
        'price_for_two': 450,
        'address': 'Bandra West, Mumbai',
        'is_pure_veg': True,
        'emoji': '🥗',
        'gradient': 'linear-gradient(135deg, #86efac, #16a34a)',
        'menu': {
            'Salads': [
                ('Greek Salad', 'Feta, olives, cucumber, cherry tomato', 249, True, True, '🥗'),
                ('Quinoa Power Bowl', 'Quinoa, chickpea, avocado, pumpkin seeds', 299, True, True, '🥣'),
                ('Paneer Caesar Salad', 'Grilled paneer, romaine, parmesan', 279, True, False, '🧀'),
            ],
            'Smoothies': [
                ('Tropical Mango Smoothie', 'Mango, banana, yoghurt', 149, True, True, '🥭'),
                ('Berry Blast', 'Mixed berries with almond milk', 179, True, False, '🍇'),
            ],
        },
    },
    {
        'name': 'Punjabi Tandoor',
        'cuisine': 'North Indian, Tandoori, Mughlai',
        'rating': '4.5',
        'rating_count': 16800,
        'delivery_minutes': 35,
        'price_for_two': 500,
        'address': 'Rajouri Garden, New Delhi',
        'promoted': True,
        'offer_text': '60% OFF up to ₹120',
        'emoji': '🫓',
        'gradient': 'linear-gradient(135deg, #fdba74, #c2410c)',
        'menu': {
            'Starters': [
                ('Tandoori Chicken (Half)', 'Charcoal-grilled with mint chutney', 279, False, True, '🍗'),
                ('Paneer Tikka', 'Smoky spiced paneer cubes', 249, True, True, '🧀'),
                ('Honey Chilli Potato', 'Crispy potato tossed in honey chilli', 189, True, False, '🍯'),
            ],
            'Main Course': [
                ('Butter Chicken', 'Creamy tomato gravy with tandoori chicken', 329, False, True, '🍛'),
                ('Dal Makhani', 'Slow-cooked black lentils, butter', 229, True, True, '🍲'),
                ('Paneer Butter Masala', 'Rich cashew tomato gravy', 259, True, True, '🍲'),
                ('Garlic Naan', 'Tandoor-fresh naan with garlic butter', 59, True, True, '🫓'),
            ],
        },
    },
    {
        'name': 'Roll Royce',
        'cuisine': 'Rolls, Kebabs, Street Food',
        'rating': '4.2',
        'rating_count': 7800,
        'delivery_minutes': 24,
        'price_for_two': 250,
        'address': 'Park Street, Kolkata',
        'offer_text': 'Flat ₹75 OFF',
        'emoji': '🌯',
        'gradient': 'linear-gradient(135deg, #fca5a5, #b91c1c)',
        'menu': {
            'Kathi Rolls': [
                ('Chicken Kathi Roll', 'Double egg chicken roll with onions', 149, False, True, '🌯'),
                ('Paneer Tikka Roll', 'Charred paneer in flaky paratha', 129, True, True, '🌯'),
                ('Egg Roll', 'Classic Kolkata egg roll', 79, False, False, '🥚'),
                ('Mutton Seekh Roll', 'Minced mutton kebab wrap', 199, False, False, '🌯'),
            ],
            'Kebabs': [
                ('Chicken Seekh Kebab (4)', 'Juicy minced chicken skewers', 229, False, True, '🍢'),
                ('Aloo Kabab (4)', 'Crispy potato patties', 99, True, False, '🥔'),
            ],
        },
    },
    {
        'name': 'Sweet Tooth Bakery',
        'cuisine': 'Desserts, Bakery, Ice Cream',
        'rating': '4.7',
        'rating_count': 9300,
        'delivery_minutes': 15,
        'price_for_two': 200,
        'address': 'Jubilee Hills, Hyderabad',
        'is_pure_veg': True,
        'offer_text': 'Buy 2 Get 1 on pastries',
        'emoji': '🍰',
        'gradient': 'linear-gradient(135deg, #f9a8d4, #db2777)',
        'menu': {
            'Pastries & Cakes': [
                ('Chocolate Truffle Pastry', 'Rich dark chocolate ganache', 99, True, True, '🍰'),
                ('Red Velvet Pastry', 'Cream cheese frosting', 119, True, True, '🧁'),
                ('Blueberry Cheesecake Slice', 'Baked NY-style cheesecake', 149, True, False, '🫐'),
            ],
            'Ice Creams': [
                ('Belgian Choco Scoop (2)', 'Double scoops with choco chips', 129, True, True, '🍨'),
                ('Mango Kulfi', 'Traditional dense kulfi', 89, True, False, '🥭'),
            ],
        },
    },
    {
        'name': 'Chai Point Sides',
        'cuisine': 'Beverages, Snacks, Cafe',
        'rating': '3.9',
        'rating_count': 3600,
        'delivery_minutes': 16,
        'price_for_two': 150,
        'address': 'Hauz Khas Village, New Delhi',
        'is_open': False,
        'emoji': '☕',
        'gradient': 'linear-gradient(135deg, #d6b48a, #92400e)',
        'menu': {
            'Chai & Coffee': [
                ('Masala Chai', 'Spiced Indian tea', 39, True, True, '☕'),
                ('Cutting Chai', 'Strong Mumbai-style shot', 25, True, False, '☕'),
                ('Cold Coffee with Ice Cream', 'Frothy coffee topped with a scoop', 119, True, False, '🧋'),
            ],
            'Snacks': [
                ('Bun Maska', 'Soft bun with generous butter', 49, True, False, '🍞'),
                ('Vada Pav', 'Mumbai classic with chutney', 45, True, True, '🥪'),
                ('Samosa (2 pcs)', 'Crunchy potato filling', 40, True, False, '🥟'),
            ],
        },
    },
]


class Command(BaseCommand):
    help = 'Seed FoodFlow with Swiggy-style restaurants, menus and demo users.'

    def add_arguments(self, parser):
        parser.add_argument('--flush', action='store_true', help='Delete existing data first.')

    def handle(self, *args, **options):
        if options['flush']:
            MenuItem.objects.all().delete()
            MenuCategory.objects.all().delete()
            Restaurant.objects.all().delete()
            self.stdout.write(self.style.WARNING('Flushed existing restaurants and menus.'))

        created_count = 0
        for index, entry in enumerate(RESTAURANTS, start=1):
            if Restaurant.objects.filter(name=entry['name']).exists():
                self.stdout.write(f'  skip: {entry["name"]} (already exists)')
                continue
            menu = entry['menu']
            fields = {key: value for key, value in entry.items() if key != 'menu'}
            restaurant = Restaurant.objects.create(**fields)
            for category_order, (category_name, items) in enumerate(menu.items()):
                category = MenuCategory.objects.create(
                    restaurant=restaurant, name=category_name, order=category_order
                )
                for name, description, price, is_veg, is_bestseller, emoji in items:
                    MenuItem.objects.create(
                        restaurant=restaurant,
                        category=category,
                        name=name,
                        description=description,
                        price=price,
                        is_veg=is_veg,
                        is_bestseller=is_bestseller,
                        emoji=emoji,
                    )
            created_count += 1
            self.stdout.write(self.style.SUCCESS(f'  created: {restaurant.name} ({sum(len(v) for v in menu.values())} items)'))

        # Demo users ---------------------------------------------------------
        if not User.objects.filter(email='admin@foodflow.app').exists():
            User.objects.create_superuser(
                email='admin@foodflow.app', password='admin123', first_name='FoodFlow Admin'
            )
            self.stdout.write(self.style.SUCCESS('  created admin: admin@foodflow.app / admin123'))
        if not User.objects.filter(email='demo@foodflow.app').exists():
            User.objects.create_user(
                email='demo@foodflow.app', password='demo1234', first_name='Demo Foodie', phone='9876543210'
            )
            self.stdout.write(self.style.SUCCESS('  created demo user: demo@foodflow.app / demo1234'))

        self.stdout.write(self.style.SUCCESS(f'Seed complete: {created_count} new restaurants.'))
