import logging
from datetime import datetime

import requests
from django.shortcuts import redirect, render
from staff.roles import role_of

from . import api_client
from .api import delete, get, patch, post
from .constants import CATEGORIES, PRIORITIES, STATUSES

logger = logging.getLogger(__name__)


def home(request):
    """Home page: the signed-in staff member's role and the support request counts."""
    try:
        counts = api_client.request_counts()
    except api_client.ApiUnavailable:
        logger.warning("Dashboard counts unavailable", exc_info=True)
        counts = None
    return render(
        request,
        "dashboard/home.html",
        {"role": role_of(request.user), "counts": counts},
    )


def request_dashboard(request):
    """Display and filter support requests."""

    filters = {
        "category": request.GET.get("category", "").strip(),
        "status": request.GET.get("status", "").strip(),
        "operational_priority": request.GET.get("priority", "").strip(),
        "area_id": request.GET.get("area_id", "").strip(),
        "search": request.GET.get("search", "").strip(),
    }

    # Only send filters that have values.
    params = {key: value for key, value in filters.items() if value}

    support_requests = []
    areas = []
    error = None

    # Retrieve filtered support requests.
    try:
        response = get("/api/requests/", params=params)
        response.raise_for_status()
        support_requests = response.json()

        for item in support_requests:
            if item.get("created_at"):
                item["created_at"] = datetime.fromisoformat(item["created_at"])

    except requests.RequestException:
        logger.warning(
            "Could not retrieve support requests",
            exc_info=True,
        )
        error = "Support requests are currently unavailable."

    # Retrieve areas for the area dropdown.
    try:
        areas_response = get("/api/areas/")
        areas_response.raise_for_status()
        areas = areas_response.json()

    except requests.RequestException:
        logger.warning("Could not retrieve areas", exc_info=True)
        error = error or "Area information is currently unavailable."

    return render(
        request,
        "dashboard/requests/dashboard.html",
        {
            "support_requests": support_requests,
            "areas": areas,
            "category_choices": CATEGORIES,
            "status_choices": STATUSES,
            "priority_choices": PRIORITIES,
            "error": error,
        },
    )


def request_detail(request, reference):
    """Display details of an individual support request."""
    try:
        response = get(f"/api/requests/{reference}")
        response.raise_for_status()

        support_request = response.json()
        error = None

        if support_request.get("created_at"):
            support_request["created_at"] = datetime.fromisoformat(
                support_request["created_at"]
            )

    except requests.HTTPError as exc:
        logger.warning(
            "Could not retrieve support request %s: %s",
            reference,
            exc,
        )

        support_request = None

        if exc.response is not None and exc.response.status_code == 404:
            error = "Support request not found."
        else:
            error = "Could not retrieve this support request."

    except requests.RequestException:
        logger.warning(
            "Flask API unavailable for support request %s",
            reference,
            exc_info=True,
        )
        support_request = None
        error = "The support request service is currently unavailable."

    return render(
        request,
        "dashboard/requests/detail.html",
        {
            "request_id": reference,
            "support_request": support_request,
            "error": error,
        },
    )


def request_create(request):
    """Display and process the create support request form."""

    errors = []
    residents = []
    areas = []

    try:
        residents_response = get("/api/residents/")
        residents_response.raise_for_status()
        residents = residents_response.json()

        areas_response = get("/api/areas/")
        areas_response.raise_for_status()
        areas = areas_response.json()

    except requests.RequestException:
        logger.warning("Could not load residents or areas", exc_info=True)
        errors.append(
            "Could not load resident or area information. "
            "Please check that the Flask API is running."
        )

    if request.method == "POST" and not errors:
        add_new_resident = request.POST.get("add_new_resident") == "yes"

        # Create a resident first if the staff member chose that option.
        resident_id = request.POST.get("resident_id", "")

        if add_new_resident:
            resident_data = {
                "display_name": request.POST.get("new_resident_name", "").strip(),
                "contact_phone": request.POST.get("new_resident_phone", "").strip()
                or None,
                "postcode": request.POST.get("new_resident_postcode", "").strip()
                or None,
            }

            if not resident_data["display_name"]:
                errors.append("Please enter the new resident's name.")

            if not errors:
                try:
                    resident_response = post(
                        "/api/residents/",
                        json=resident_data,
                    )
                    resident_response.raise_for_status()
                    resident_id = resident_response.json()["id"]

                except requests.HTTPError:
                    logger.warning("Flask rejected the new resident", exc_info=True)
                    errors.append("The new resident could not be saved.")

                except (requests.RequestException, ValueError, KeyError):
                    logger.warning("Could not create new resident", exc_info=True)
                    errors.append("The resident service is currently unavailable.")

        elif not resident_id:
            errors.append("Please select a resident or add a new one.")

        data = {
            "description": request.POST.get("description", "").strip(),
            "category": request.POST.get("category", ""),
            "resident_id": resident_id,
            "area_id": request.POST.get("area_id") or None,
            "operational_priority": request.POST.get("operational_priority", "normal"),
            "status": request.POST.get("status", "pending"),
        }

        # if not data["reference"]:
        #     errors.append("Please enter a request reference.")

        if not data["description"]:
            errors.append("Please enter a description.")

        if data["category"] not in [value for value, label in CATEGORIES]:
            errors.append("Please select a valid category.")

        if data["operational_priority"] not in [value for value, label in PRIORITIES]:
            errors.append("Please select a valid priority.")

        if data["status"] not in [value for value, label in STATUSES]:
            errors.append("Please select a valid status.")

        try:
            data["resident_id"] = int(data["resident_id"])
        except (TypeError, ValueError):
            errors.append("Please select a valid resident.")

        if data["area_id"] is not None:
            try:
                data["area_id"] = int(data["area_id"])
            except (TypeError, ValueError):
                errors.append("Please select a valid area.")

        if not errors:
            try:
                response = post("/api/requests/", json=data)
                response.raise_for_status()

                created_request = response.json()
                print(created_request)
                return redirect(
                    "request_detail",
                    reference=created_request["reference"],
                )

            except requests.HTTPError:
                logger.warning(
                    "Flask rejected the new support request",
                    exc_info=True,
                )
                errors.append(
                    "The support request could not be created. "
                    "Please check the information and try again."
                )

            except requests.RequestException:
                logger.warning(
                    "Could not submit support request",
                    exc_info=True,
                )
                errors.append("The support request service is currently unavailable.")

    return render(
        request,
        "dashboard/requests/create.html",
        {
            "residents": residents,
            "areas": areas,
            "categories": CATEGORIES,
            "priorities": PRIORITIES,
            "statuses": STATUSES,
            "errors": errors,
        },
    )


def request_edit(request, reference):
    """Display and process the edit support request form."""

    errors = []
    support_request = None
    areas = []

    try:
        response = get(f"/api/requests/{reference}")
        response.raise_for_status()
        support_request = response.json()

        areas_response = get("/api/areas/")
        areas_response.raise_for_status()
        areas = areas_response.json()

    except requests.HTTPError as exc:
        logger.warning(
            "Could not retrieve request %s",
            reference,
            exc_info=True,
        )

        if exc.response is not None and exc.response.status_code == 404:
            return render(
                request,
                "dashboard/requests/edit.html",
                {
                    "error": "Support request not found.",
                    "request_id": reference,
                },
                status=404,
            )

        errors.append("Could not retrieve the support request.")

    except requests.RequestException:
        logger.warning("Flask API unavailable", exc_info=True)
        errors.append("The support request service is currently unavailable.")

    if request.method == "POST" and support_request:
        data = {
            "description": request.POST.get("description", "").strip(),
            "category": request.POST.get("category", ""),
            "area_id": request.POST.get("area_id") or None,
            "operational_priority": request.POST.get("operational_priority", ""),
            "status": request.POST.get("status", ""),
        }

        if not data["description"]:
            errors.append("Please enter a description.")

        if data["category"] not in [value for value, label in CATEGORIES]:
            errors.append("Please select a valid category.")

        if data["operational_priority"] not in [value for value, label in PRIORITIES]:
            errors.append("Please select a valid priority.")

        if data["status"] not in [value for value, label in STATUSES]:
            errors.append("Please select a valid status.")

        if data["area_id"] is not None:
            try:
                data["area_id"] = int(data["area_id"])
            except (TypeError, ValueError):
                errors.append("Please select a valid area.")

        if not errors:
            try:
                update_response = patch(
                    f"/api/requests/{reference}",
                    json=data,
                    headers={"X-HTTP-Method-Override": "PATCH"},
                )

                print("DATA SENT TO FLASK:", data)
                print("FLASK STATUS:", update_response.status_code)
                print("FLASK RESPONSE:", update_response.text)
                # Use the actual PATCH method rather than method override.
                update_response.raise_for_status()

                return redirect(
                    "request_detail",
                    reference,
                )

            except requests.RequestException:
                logger.warning(
                    "Could not update support request %s",
                    reference,
                    exc_info=True,
                )
                errors.append("The support request could not be updated.")

        # Preserve submitted values when validation fails.
        support_request.update(data)

    return render(
        request,
        "dashboard/requests/edit.html",
        {
            "support_request": support_request,
            "areas": areas,
            "categories": CATEGORIES,
            "priorities": PRIORITIES,
            "statuses": STATUSES,
            "errors": errors,
        },
    )


def request_delete(request, reference):
    """Delete an existing support request."""

    if request.method == "POST":
        try:
            response = delete(f"/api/requests/{reference}")
            response.raise_for_status()
            return redirect("request_dashboard")

        except requests.HTTPError as exc:
            logger.warning(
                "Could not delete support request %s: %s",
                reference,
                exc,
            )
            error = "Could not delete this support request."

        except requests.RequestException:
            logger.warning(
                "Flask API unavailable while deleting request %s",
                reference,
                exc_info=True,
            )
            error = "The support request service is currently unavailable."

        return render(
            request,
            "dashboard/requests/delete_error.html",
            {"reference": reference, "error": error},
        )

    return redirect("request_detail", reference)


def cooling_centre_dashboard(request):
    centres_response = get("/api/centres/")
    areas_response = get("/api/areas/")

    centres = []
    areas_by_id = {}

    if centres_response.ok:
        centres = centres_response.json()

    if areas_response.ok:
        areas = areas_response.json()
        areas_by_id = {area["id"]: area.get("name", "Unknown area") for area in areas}

    for centre in centres:
        centre["area_name"] = areas_by_id.get(
            centre.get("area_id"),
            "Unknown area",
        )

    return render(
        request,
        "dashboard/cooling_centres/dashboard.html",
        {"centres": centres},
    )


def cooling_centre_create(request):
    areas_response = get("/api/areas/")
    areas = areas_response.json() if areas_response.ok else []
    errors = []

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        location = request.POST.get("location", "").strip()
        status = request.POST.get("status", "open")
        capacity_value = request.POST.get("capacity", "").strip()
        add_new_area = request.POST.get("add_new_area") == "yes"

        try:
            capacity = int(capacity_value)
            if capacity < 1:
                raise ValueError
        except ValueError:
            errors.append("Enter a capacity of at least 1.")
            capacity = None

        area_id = None

        if add_new_area:
            new_area_name = request.POST.get("new_area_name", "").strip()

            if not new_area_name:
                errors.append("Enter a name for the new area.")
            else:
                area_response = post(
                    "/api/areas/",
                    json={"name": new_area_name},
                )

                if area_response.status_code == 201:
                    area_id = area_response.json()["id"]
                else:
                    try:
                        errors.append(
                            area_response.json().get(
                                "message",
                                "Could not create the area.",
                            )
                        )
                    except ValueError:
                        errors.append("Could not create the area.")
        else:
            area_id_value = request.POST.get("area_id", "").strip()

            try:
                area_id = int(area_id_value)
            except (TypeError, ValueError):
                errors.append("Select an area.")

        if not name:
            errors.append("Enter a cooling-centre name.")

        if not location:
            errors.append("Enter the centre location.")

        if not errors:
            centre_response = post(
                "/api/centres/",
                json={
                    "name": name,
                    "location": location,
                    "status": status,
                    "capacity": capacity,
                    "area_id": area_id,
                },
            )

            if centre_response.status_code == 201:
                return redirect("cooling_centre_dashboard")

            try:
                errors.append(
                    centre_response.json().get(
                        "message",
                        "Could not create the cooling centre.",
                    )
                )
            except ValueError:
                errors.append("Could not create the cooling centre.")

        # Refresh the list so a newly-created area appears in the dropdown.
        areas_response = get("/api/areas/")
        areas = areas_response.json() if areas_response.ok else []

    return render(
        request,
        "dashboard/cooling_centres/create.html",
        {
            "areas": areas,
            "errors": errors,
            "form_data": request.POST,
        },
    )


def cooling_centre_details(request, centre_id):
    """Display details of an individual cooling centre."""

    centre = None
    error = None

    try:
        response = get(f"/api/centres/{centre_id}")
        response.raise_for_status()
        centre = response.json()

        areas_response = get("/api/areas/")
        areas_response.raise_for_status()
        areas = areas_response.json()

        area_names = {area["id"]: area.get("name", "Unknown area") for area in areas}
        centre["area_name"] = area_names.get(
            centre.get("area_id"),
            "Not specified",
        )

    except requests.HTTPError as exc:
        logger.warning(
            "Could not retrieve cooling centre %s: %s",
            centre_id,
            exc,
        )

        if exc.response is not None and exc.response.status_code == 404:
            error = "Cooling centre not found."
        else:
            error = "Could not retrieve this cooling centre."

    except requests.RequestException:
        logger.warning(
            "Flask API unavailable for cooling centre %s",
            centre_id,
            exc_info=True,
        )
        error = "The cooling centre service is currently unavailable."

    return render(
        request,
        "dashboard/cooling_centres/details.html",
        {
            "centre_id": centre_id,
            "centre": centre,
            "error": error,
        },
    )


def cooling_centre_edit(request, centre_id):
    """Display and process the edit cooling centre form."""

    errors = []
    centre = None
    areas = []

    try:
        response = get(f"/api/centres/{centre_id}")
        response.raise_for_status()
        centre = response.json()

        areas_response = get("/api/areas/")
        areas_response.raise_for_status()
        areas = areas_response.json()

    except requests.HTTPError as exc:
        logger.warning(
            "Could not retrieve cooling centre %s: %s",
            centre_id,
            exc,
            exc_info=True,
        )

        if exc.response is not None and exc.response.status_code == 404:
            return render(
                request,
                "dashboard/cooling-centre/edit.html",
                {
                    "centre_id": centre_id,
                    "error": "Cooling centre not found.",
                },
                status=404,
            )

        errors.append("Could not retrieve the cooling centre.")

    except requests.RequestException:
        logger.warning(
            "Flask API unavailable for cooling centre %s",
            centre_id,
            exc_info=True,
        )
        errors.append("The cooling centre service is currently unavailable.")

    if request.method == "POST" and centre:
        data = {
            "name": request.POST.get("name", "").strip(),
            "location": request.POST.get("location", "").strip(),
            "status": request.POST.get("status", ""),
            "capacity": request.POST.get("capacity", "").strip(),
        }

        add_new_area = request.POST.get("add_new_area") == "yes"
        area_id_value = request.POST.get("area_id", "").strip()
        new_area_name = request.POST.get("new_area_name", "").strip()

        if not data["name"]:
            errors.append("Enter a cooling-centre name.")

        if not data["location"]:
            errors.append("Enter the centre location.")

        if data["status"] not in ["open", "closed"]:
            errors.append("Select a valid status.")

        try:
            data["capacity"] = int(data["capacity"])
            if data["capacity"] < 1:
                raise ValueError
        except (TypeError, ValueError):
            errors.append("Enter a capacity of at least 1.")

        if add_new_area:
            if not new_area_name:
                errors.append("Enter a name for the new area.")
        else:
            try:
                data["area_id"] = int(area_id_value)
            except (TypeError, ValueError):
                errors.append("Select an area.")

        # Only create the new area after the centre fields pass validation.
        if not errors and add_new_area:
            try:
                area_response = post(
                    "/api/areas/",
                    json={"name": new_area_name},
                )
                area_response.raise_for_status()
                data["area_id"] = area_response.json()["id"]

            except requests.HTTPError:
                logger.warning("Flask rejected the new area", exc_info=True)
                errors.append("The new area could not be created.")

            except (requests.RequestException, ValueError, KeyError):
                logger.warning("Could not create the new area", exc_info=True)
                errors.append("The area service is currently unavailable.")

        if not errors:
            try:
                update_response = patch(
                    f"/api/centres/{centre_id}",
                    json=data,
                )
                update_response.raise_for_status()

                return redirect("cooling_centre_details", centre_id=centre_id)

            except requests.HTTPError:
                logger.warning(
                    "Flask rejected update for cooling centre %s",
                    centre_id,
                    exc_info=True,
                )
                errors.append("The cooling centre could not be updated.")

            except requests.RequestException:
                logger.warning(
                    "Could not update cooling centre %s",
                    centre_id,
                    exc_info=True,
                )
                errors.append("The cooling centre service is currently unavailable.")

        # Preserve submitted values when validation or saving fails.
        centre.update(data)
        centre["add_new_area"] = add_new_area
        centre["new_area_name"] = new_area_name

        # Reload areas in case a new area was created.
        try:
            areas_response = get("/api/areas/")
            areas_response.raise_for_status()
            areas = areas_response.json()
        except requests.RequestException:
            logger.warning("Could not reload areas", exc_info=True)

    return render(
        request,
        "dashboard/cooling_centres/edit.html",
        {
            "centre": centre,
            "areas": areas,
            "errors": errors,
        },
    )
