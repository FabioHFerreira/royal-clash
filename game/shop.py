# Criar o arquivo shop.py
cat > game/shop.py << 'EOL'
import json
from datetime import datetime, timedelta
import random
from PIL import Image, ImageTk

class ShopItem:
    def __init__(self, id, name, description, cost, item_type, rarity=None, quantity=1, image_path=None):
        self.id = id
        self.name = name
        self.description = description
        self.cost = cost
        self.item_type = item_type  # "card", "chest", "gold", "gems"
        self.rarity = rarity
        self.quantity = quantity
        self.image = None
        self.image_path = image_path
        self.load_image()

    def load_image(self):
        if self.image_path:
            try:
                self.image = Image.open(self.image_path)
                self.image = self.image.resize((150, 200))
            except FileNotFoundError:
                self.image = Image.new('RGB', (150, 200), color='gray')
        else:
            self.image = Image.new('RGB', (150, 200), color='gray')

class Shop:
    def __init__(self):
        self.items = []
        self.daily_offers = []
        self.special_offers = []
        self.load_shop_data()
        self.update_offers()

    def load_shop_data(self):
        try:
            with open("data/shop.json", "r") as f:
                data = json.load(f)
                self.items = [ShopItem(**item) for item in data.get("items", [])]
                self.daily_offers = [ShopItem(**offer) for offer in data.get("daily_offers", [])]
                self.special_offers = [ShopItem(**offer) for offer in data.get("special_offers", [])]
        except FileNotFoundError:
            self._create_default_shop()

    def _create_default_shop(self):
        self.items = [
            ShopItem(
                "gold_1000",
                "Gold Pack",
                "1000 Gold",
                100,
                "gold",
                quantity=1000,
                image_path="assets/shop/gold_pack.png"
            ),
            ShopItem(
                "gold_5000",
                "Gold Pack",
                "5000 Gold",
                450,
                "gold",
                quantity=5000,
                image_path="assets/shop/gold_pack.png"
            ),
            ShopItem(
                "gems_100",
                "Gems Pack",
                "100 Gems",
                100,
                "gems",
                quantity=100,
                image_path="assets/shop/gems_pack.png"
            ),
            ShopItem(
                "gems_500",
                "Gems Pack",
                "500 Gems",
                450,
                "gems",
                quantity=500,
                image_path="assets/shop/gems_pack.png"
            ),
            ShopItem(
                "common_chest",
                "Common Chest",
                "Contains 3 Common Cards",
                50,
                "chest",
                "Common",
                image_path="assets/shop/common_chest.png"
            ),
            ShopItem(
                "rare_chest",
                "Rare Chest",
                "Contains 2 Rare Cards",
                150,
                "chest",
                "Rare",
                image_path="assets/shop/rare_chest.png"
            ),
            ShopItem(
                "epic_chest",
                "Epic Chest",
                "Contains 1 Epic Card",
                300,
                "chest",
                "Epic",
                image_path="assets/shop/epic_chest.png"
            ),
            ShopItem(
                "legendary_chest",
                "Legendary Chest",
                "Contains 1 Legendary Card",
                500,
                "chest",
                "Legendary",
                image_path="assets/shop/legendary_chest.png"
            )
        ]

        self.save_shop_data()

    def save_shop_data(self):
        data = {
            "items": [vars(item) for item in self.items],
            "daily_offers": [vars(offer) for offer in self.daily_offers],
            "special_offers": [vars(offer) for offer in self.special_offers]
        }
        with open("data/shop.json", "w") as f:
            json.dump(data, f, indent=4)

    def update_offers(self):
        # Update daily offers
        self.daily_offers = [
            ShopItem(
                "daily_chest",
                "Daily Chest",
                "Special daily chest",
                0,
                "chest",
                "Common",
                image_path="assets/shop/daily_chest.png"
            ),
            ShopItem(
                "daily_gold",
                "Daily Gold",
                "100 Gold",
                0,
                "gold",
                quantity=100,
                image_path="assets/shop/daily_gold.png"
            )
        ]

        # Update special offers (randomly)
        if random.random() < 0.3:  # 30% chance to have a special offer
            self.special_offers = [
                ShopItem(
                    "special_chest",
                    "Special Chest",
                    "Limited time offer!",
                    200,
                    "chest",
                    "Epic",
                    image_path="assets/shop/special_chest.png"
                ),
                ShopItem(
                    "special_gems",
                    "Special Gems",
                    "Double gems!",
                    200,
                    "gems",
                    quantity=200,
                    image_path="assets/shop/special_gems.png"
                )
            ]
        else:
            self.special_offers = []

        self.save_shop_data()

    def purchase_item(self, player, item_id):
        item = next((item for item in self.items + self.daily_offers + self.special_offers if item.id == item_id), None)
        if not item:
            return False, "Item not found"

        if item.cost > player.gems:
            return False, "Not enough gems"

        player.spend_gems(item.cost)
        
        if item.item_type == "gold":
            player.earn_gold(item.quantity)
        elif item.item_type == "gems":
            player.earn_gems(item.quantity)
        elif item.item_type == "chest":
            player.add_chest(item.rarity, datetime.now() + timedelta(hours=3))

        return True, "Purchase successful"

    def get_available_items(self):
        return {
            "regular": self.items,
            "daily": self.daily_offers,
            "special": self.special_offers
        }

class MicrotransactionManager:
    def __init__(self):
        self.packages = {
            "starter": {
                "gems": 100,
                "price": 4.99,
                "bonus": 0,
                "image": "assets/shop/starter_pack.png"
            },
            "premium": {
                "gems": 500,
                "price": 19.99,
                "bonus": 50,
                "image": "assets/shop/premium_pack.png"
            },
            "deluxe": {
                "gems": 1200,
                "price": 49.99,
                "bonus": 200,
                "image": "assets/shop/deluxe_pack.png"
            },
            "ultimate": {
                "gems": 2500,
                "price": 99.99,
                "bonus": 500,
                "image": "assets/shop/ultimate_pack.png"
            }
        }

    def process_purchase(self, player, package_id):
        if package_id not in self.packages:
            return False, "Invalid package"

        package = self.packages[package_id]
        total_gems = package["gems"] + package["bonus"]
        player.earn_gems(total_gems)
        return True, f"Successfully purchased {total_gems} gems (including {package['bonus']} bonus gems)"

    def get_available_packages(self):
        return self.packages
