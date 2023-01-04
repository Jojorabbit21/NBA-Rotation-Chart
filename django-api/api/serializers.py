from rest_framework import serializers

class ApiSerializer(serializers.ModelSerializer):
    class Meta:
        model = None
        fields = None