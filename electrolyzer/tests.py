from django.test import TestCase
from django.urls import reverse
from .models import PartType

# Create your tests here.
class ElectrolyzerTypeTestCase(TestCase):
    def setUp(self):
        self.electrolyzer_type = PartType.objects.create(name='Type 1')

    def test_add_electrolyzer_type(self):
        url = reverse('add_electrolyzer_type')
        data = {'name': 'Type 2'}

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'message': 'Тип добавлен'})

        # Check if the electrolyzer type was created in the database
        electrolyzer_type = PartType.objects.filter(name='Type 2').first()
        self.assertIsNotNone(electrolyzer_type)


