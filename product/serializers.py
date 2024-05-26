from rest_framework import serializers

from .models import Brand, Category, PrivateCategory, Product


class CategorySerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source="parent.name", read_only=True)
    parent_slug = serializers.CharField(source="parent.slug", read_only=True)
    children_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = "__all__"

    def get_children_count(self, obj):
        return obj.get_descendant_count()


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    brand = BrandSerializer()

    class Meta:
        model = Product
        fields = "__all__"


class PrivateCategorySerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True)

    class Meta:
        model = PrivateCategory
        fields = "__all__"
