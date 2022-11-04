import gspread
import os
import json

def upload_csv_to_google_spreadsheet(csv_string, spreadsheet_id):
    credentials = json.loads(os.environ['GOOGLE_CLOUD_SERVICE_ACCOUNT_KEY'])

    gc = gspread.service_account_from_dict(credentials)

    gc.import_csv(spreadsheet_id, data=csv_string)


def run_spreadsheet_migrations():
    from api.models import GuidedFlow, ShowSelectMenu, ShowCustomModal
    from api.admin.guided_flow_admin import export_flow_submissions
    from api.admin.guided_flow_step_admin import export_menu_submissions_to_csv, export_modal_submissions_to_csv

    flow_count = 0
    for flow in GuidedFlow.objects.filter(google_spreadsheet_id__isnull=False).exclude(google_spreadsheet_id__exact=""):
        spreadsheet_id = flow.google_spreadsheet_id
        qs = GuidedFlow.objects.filter(id=flow.id)
        csv_result = export_flow_submissions(qs, only_latest=False)
        upload_csv_to_google_spreadsheet(csv_result.getvalue(), spreadsheet_id)

        flow_count += 1

    menu_count = 0
    for menu in ShowSelectMenu.objects.filter(google_spreadsheet_id__isnull=False).exclude(
            google_spreadsheet_id__exact=""):
        spreadsheet_id = menu.google_spreadsheet_id
        qs = ShowSelectMenu.objects.filter(id=menu.id)
        csv_result = export_menu_submissions_to_csv(qs)
        upload_csv_to_google_spreadsheet(csv_result.getvalue(), spreadsheet_id)

        menu_count += 1

    modal_count = 0
    for modal in ShowCustomModal.objects.filter(google_spreadsheet_id__isnull=False).exclude(
            google_spreadsheet_id__exact=""):
        spreadsheet_id = modal.google_spreadsheet_id
        qs = ShowCustomModal.objects.filter(id=modal.id)
        csv_result = export_modal_submissions_to_csv(qs)
        upload_csv_to_google_spreadsheet(csv_result.getvalue(), spreadsheet_id)

        modal_count += 1

    return {
        "success": True,
        "flow_count": flow_count,
        "menu_count": menu_count,
        "modal_count": modal_count
    }
