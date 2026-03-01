import csv

from django.core.management.base import BaseCommand, CommandError

from models.state import State
from models.district import District


class Command(BaseCommand):
    help = "Seed State/District master from CSV with LGD codes"

    def add_arguments(self, parser):
        parser.add_argument("--file", required=True, help="CSV file path")

    def handle(self, *args, **options):
        file_path = options["file"]

        created_states = 0
        updated_states = 0
        created_districts = 0
        updated_districts = 0

        try:
            with open(file_path, "r", encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle)

                required_any = {
                    "state_name", "state", "state_lgd_code", "state_code",
                    "district_name", "district", "district_lgd_code", "district_code",
                }
                if not reader.fieldnames or not any(col in reader.fieldnames for col in required_any):
                    raise CommandError(
                        "Invalid CSV headers. Expected columns such as state_name/state, state_lgd_code/state_code, "
                        "district_name/district, district_lgd_code/district_code"
                    )

                for idx, row in enumerate(reader, start=2):
                    state_name = (row.get("state_name") or row.get("state") or "").strip()
                    state_lgd_code = (row.get("state_lgd_code") or row.get("state_code") or "").strip()

                    district_name = (row.get("district_name") or row.get("district") or "").strip()
                    district_lgd_code = (row.get("district_lgd_code") or row.get("district_code") or "").strip()

                    if not state_name:
                        raise CommandError(f"Row {idx}: state_name/state is required")
                    if not district_name:
                        raise CommandError(f"Row {idx}: district_name/district is required")

                    state_obj = None
                    if state_lgd_code:
                        state_obj = State.objects.filter(lgd_code=state_lgd_code).first()

                    if not state_obj:
                        state_obj = State.objects.filter(name__iexact=state_name).first()

                    if not state_obj:
                        state_obj = State.objects.create(name=state_name, lgd_code=state_lgd_code or None)
                        created_states += 1
                    else:
                        dirty = False
                        if state_obj.name != state_name:
                            state_obj.name = state_name
                            dirty = True
                        if state_lgd_code and state_obj.lgd_code != state_lgd_code:
                            state_obj.lgd_code = state_lgd_code
                            dirty = True
                        if dirty:
                            state_obj.save(update_fields=["name", "lgd_code"])
                            updated_states += 1

                    district_obj = None
                    if district_lgd_code:
                        district_obj = District.objects.filter(lgd_code=district_lgd_code).first()

                    if not district_obj:
                        district_obj = District.objects.filter(name__iexact=district_name, state=state_obj).first()

                    if not district_obj:
                        District.objects.create(
                            name=district_name,
                            state=state_obj,
                            lgd_code=district_lgd_code or None,
                        )
                        created_districts += 1
                    else:
                        dirty = False
                        if district_obj.name != district_name:
                            district_obj.name = district_name
                            dirty = True
                        if district_obj.state_id != state_obj.id:
                            district_obj.state = state_obj
                            dirty = True
                        if district_lgd_code and district_obj.lgd_code != district_lgd_code:
                            district_obj.lgd_code = district_lgd_code
                            dirty = True
                        if dirty:
                            district_obj.save(update_fields=["name", "state", "lgd_code"])
                            updated_districts += 1

        except FileNotFoundError as exc:
            raise CommandError(f"File not found: {file_path}") from exc

        self.stdout.write(
            self.style.SUCCESS(
                "LGD seeding completed | "
                f"states created={created_states}, updated={updated_states}, "
                f"districts created={created_districts}, updated={updated_districts}"
            )
        )
