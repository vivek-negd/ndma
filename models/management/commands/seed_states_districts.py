"""
Management command to seed Indian states and districts
Usage: python manage.py seed_states_districts
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from models.state import State
from models.district import District


STATES_DISTRICTS_DATA = {
    "Andhra Pradesh": [
        "Anantapur", "Chittoor", "East Godavari", "Guntur", "Kurnool",
        "Prakasam", "Sri Potti Sriramulu Nellore", "Srikakulam", "Visakhapatnam", "Vizianagaram",
        "YSR", "West Godavari"
    ],
    "Arunachal Pradesh": [
        "Anjaw", "East Siang", "Longding", "Lower Dibang Valley", "Lower Subansiri",
        "Namsai", "Papum Pare", "Tawang", "West Kameng", "Itanagar Capital", "Pakke Kessang"
    ],
    "Assam": [
        "Baksa", "Barpeta", "Cachar", "Darrang", "Dhubri", "Dibrugarh",
        "Dima Hasao", "Hailakandi", "Karimganj", "Kokrajhar", "Morigaon",
        "Nagaon", "Nalbari", "Sivasagar", "Tinsukia", "Udalguri"
    ],
    "Bihar": [
        "Araria", "Banka", "Bhagalpur", "Darbhanga", "East Champaran", "Gopalganj",
        "Jamui", "Katihar", "Khagaria", "Kishanganj", "Lakhisarai", "Madhepura",
        "Madhubani", "Munger", "Muzaffarpur", "Nalanda", "Patna", "Purnia",
        "Saharsa", "Samastipur", "Sheohar", "Siwan", "Vaishali", "West Champaran"
    ],
    "Chhattisgarh": [
        "Korba", "Raipur", "Rajnandgaon", "Sukma"
    ],
    "Goa": [
        "North Goa", "South Goa"
    ],
    "Gujarat": [
        "Ahmedabad", "Amreli", "Anand", "Bhavnagar", "Jamnagar", "Junagadh",
        "Kheda", "Kutch", "Morbi", "Narmada", "Navsari", "Porbandar",
        "Rajkot", "Surat", "Tapi", "Vadodara", "Valsad"
    ],
    "Haryana": [
        "Faridabad", "Gurgaon", "Kurukshetra", "Mewat", "Panchkula",
        "Rewari", "Sonipat", "Yamuna Nagar"
    ],
    "Himachal Pradesh": [
        "Chamba", "Hamirpur", "Kangra", "Kinnaur", "Kullu",
        "Lahaul and Spiti", "Shimla", "Solan", "Una"
    ],
    "Jharkhand": [
        "Dumka", "Godda", "Pakur", "Sahibganj"
    ],
    "Karnataka": [
        "Bengaluru Urban", "Bagalkote", "Dakshina Kannada", "Chikamagaluru", "Kalaburagi",
        "Kodagu", "Raichur", "Shivamogga", "Udupi", "Uttara Kannada", "Yadgir"
    ],
    "Kerala": [
        "Alappuzha", "Ernakulam", "Idukki", "Kannur", "Kasaragod", "Kollam",
        "Kozhikode", "Malappuram", "Palakkad", "Pathanamthitta",
        "Thiruvananthapuram", "Wayanad"
    ],
    "Madhya Pradesh": [
        "Barwani", "Bhopal", "Chhatarpur", "Damoh", "Guna", "Khandwa (East Nimar)",
        "Raisen", "Rajgarh", "Singrauli", "Ujjain", "Vidisha"
    ],
    "Maharashtra": [
        "Ahmednagar", "Amravati", "Bhandara", "Chandrapur", "Gadchiroli", "Jalgaon",
        "Mumbai City", "Mumbai Suburban", "Nanded", "Nandurbar", "Nagpur", "Nashik",
        "Parbhani", "Pune", "Raigad", "Ratnagiri", "Sangli", "Satara", "Sindhudurg", "Thane"
    ],
    "Manipur": [
        "Bishnupur", "Churachandpur", "Chandel", "Imphal East", "Senapati",
        "Tamenglong", "Ukhrul", "Imphal West"
    ],
    "Meghalaya": [
        "East Garo Hills", "East Khasi Hills", "Ri Bhoi", "West Garo Hills", "West Khasi Hills"
    ],
    "Mizoram": [
        "Champhai", "Kolasib", "Lunglei", "Mamit", "Serchhip"
    ],
    "Nagaland": [
        "Kiphire", "Phek", "Longleng", "Mokokchung", "Peren", "Wokha", "Zunheboto"
    ],
    "Odisha": [
        "Balangir", "Balasore", "Cuttack", "Dhenkanal", "Ganjam", "Gajapati",
        "Jharsuguda", "Jajpur", "Khordha", "Kalahandi", "Kandhamal", "Koraput",
        "Kendrapara", "Malkangiri", "Nayagarh", "Rayagada"
    ],
    "Punjab": [
        "Amritsar", "Firozpur", "Faridkot", "Gurdaspur", "Hoshiarpur", "Ludhiana",
        "Pathankot", "Sahibzada Ajit Singh Nagar", "Sangrur", "Shahid Bhagat Singh Nagar",
        "Tarn Taran"
    ],
    "Rajasthan": [
        "Ajmer", "Alwar", "Bikaner", "Barmer", "Bharatpur", "Jalore", "Jodhpur",
        "Jaipur", "Jhalawar", "Kota", "Nagaur", "Pali", "Sirohi"
    ],
    "Sikkim": [
        "North Sikkim", "South Sikkim", "West Sikkim"
    ],
    "Tamil Nadu": [
        "Cuddalore", "Kanchipuram", "Kanyakumari", "Nagapattinam", "Nilgiris",
        "Pudukkottai", "Ramanathapuram", "Sivaganga", "Theni", "Tirunelveli",
        "Thanjavur", "Thoothukudi", "Tiruvallur", "Tiruvannamalai", "Viluppuram", "Virudhunagar"
    ],
    "Telangana": [
        "Adilabad", "Hyderabad", "Karimnagar", "Khammam", "Mahbubnagar",
        "Medak", "Nalgonda", "Nizamabad", "Warangal (urban)", "Warangal (rural)"
    ],
    "Tripura": [
        "Dhalai", "Gomati", "Khowai", "North Tripura", "South Tripura", "Unokoti", "West Tripura"
    ],
    "Uttar Pradesh": [
        "Amroha (Jyotiba Phule Nagar)", "Bagpat", "Bahraich", "Balrampur", "Bareilly",
        "Prayagraj", "Bulandshahr", "Deoria", "Ghaziabad", "Ghazipur", "Kushinagar",
        "Lakhimpur Kheri", "Lucknow", "Maharajganj", "Mahoba", "Meerut", "Moradabad",
        "Rampur", "Saharanpur", "Sant Kabir Nagar", "Shamli", "Shravasti",
        "Siddharthnagar", "Sonbhadra", "Varanasi"
    ],
    "Uttarakhand": [
        "Almora", "Bageshwar", "Chamoli", "Champawat", "Dehradun", "Nainital",
        "Pauri Garhwal", "Pithoragarh", "Rudraprayag", "Tehri Garhwal", "Uttarkashi"
    ],
    "West Bengal": [
        "Alipurduar", "Bankura", "Bardhaman", "Birbhum", "Cooch Behar",
        "Dakshin Dinajpur", "Darjeeling", "Hooghly", "Howrah", "Jalpaiguri",
        "Kolkata", "Maldah", "Murshidabad", "Nadia", "North 24 Parganas",
        "Kalimpong", "Uttar Dinajpur"
    ]
}


class Command(BaseCommand):
    help = "Seed Indian states and their districts with volunteer counts initialized to 0"

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Starting to seed states and districts...")
        
        created_states = 0
        created_districts = 0
        
        for state_name, districts in STATES_DISTRICTS_DATA.items():
            # Create or get state
            state, created = State.objects.get_or_create(
                name=state_name,
                defaults={
                    'volunteer_count': 0
                }
            )
            
            if created:
                created_states += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created state: {state_name}')
                )
            
            # Create districts for this state
            for district_name in districts:
                district, created = District.objects.get_or_create(
                    name=district_name,
                    state=state,
                    defaults={
                        'volunteer_count': 0
                    }
                )
                
                if created:
                    created_districts += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Seed completed successfully!\n'
                f'  - States created: {created_states}\n'
                f'  - Districts created: {created_districts}\n'
                f'  - Total states: {State.objects.count()}\n'
                f'  - Total districts: {District.objects.count()}'
            )
        )
