# ====================================================
# EventSphere - Advanced Event Management System
# Full Stack Development Project - Milestone 1
# ====================================================

import json
import os
from datetime import datetime
from typing import List, Optional


# ====================================================
# DATA CLASSES
# ====================================================

class Event:
    """Represents an event with all its attributes"""

    def __init__(
        self,
        event_id: int,
        name: str,
        event_type: str,
        date: str,
        time: str,
        budget: float = 0.0,
        description: str = ""
    ):
        self.id = event_id
        self.name = name
        self.event_type = event_type
        self.date = date
        self.time = time
        self.budget = budget
        self.description = description

        self.venue = "Not Assigned"
        self.resources = []
        self.attendees = []
        self.status = "Planning"

        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self) -> dict:
        """Convert Event object to dictionary for JSON storage"""

        return {
            "id": self.id,
            "name": self.name,
            "event_type": self.event_type,
            "date": self.date,
            "time": self.time,
            "budget": self.budget,
            "description": self.description,
            "venue": self.venue,
            "resources": self.resources,
            "attendees": self.attendees,
            "status": self.status,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Create Event object from dictionary"""

        event = cls(
            data["id"],
            data["name"],
            data["event_type"],
            data["date"],
            data["time"],
            data.get("budget", 0.0),
            data.get("description", "")
        )

        event.venue = data.get("venue", "Not Assigned")
        event.resources = data.get("resources", [])
        event.attendees = data.get("attendees", [])
        event.status = data.get("status", "Planning")
        event.created_at = data.get("created_at", "")

        return event


class Venue:
    """Represents a venue with availability tracking"""

    def __init__(
        self,
        venue_id: int,
        name: str,
        capacity: int,
        location: str,
        facilities: List[str] = None
    ):
        self.id = venue_id
        self.name = name
        self.capacity = capacity
        self.location = location
        self.facilities = facilities if facilities else []
        self.is_available = True

    def to_dict(self) -> dict:

        return {
            "id": self.id,
            "name": self.name,
            "capacity": self.capacity,
            "location": self.location,
            "facilities": self.facilities,
            "is_available": self.is_available
        }

    @classmethod
    def from_dict(cls, data: dict):

        venue = cls(
            data["id"],
            data["name"],
            data["capacity"],
            data["location"],
            data.get("facilities", [])
        )

        venue.is_available = data.get("is_available", True)

        return venue


class Resource:
    """Represents a resource with quantity tracking"""

    def __init__(
        self,
        resource_id: int,
        name: str,
        quantity: int,
        category: str = "General",
        description: str = ""
    ):
        self.id = resource_id
        self.name = name
        self.quantity = quantity
        self.category = category
        self.description = description
        self.reserved = 0

    def to_dict(self) -> dict:

        return {
            "id": self.id,
            "name": self.name,
            "quantity": self.quantity,
            "category": self.category,
            "description": self.description,
            "reserved": self.reserved
        }

    @classmethod
    def from_dict(cls, data: dict):

        resource = cls(
            data["id"],
            data["name"],
            data["quantity"],
            data.get("category", "General"),
            data.get("description", "")
        )

        resource.reserved = data.get("reserved", 0)

        return resource

    @property
    def available(self) -> int:
        """Return available resource quantity"""

        return self.quantity - self.reserved


class Attendee:
    """Represents a participant/attendee"""

    def __init__(
        self,
        attendee_id: int,
        name: str,
        email: str,
        phone: str,
        college: str = ""
    ):
        self.id = attendee_id
        self.name = name
        self.email = email
        self.phone = phone
        self.college = college

    def to_dict(self) -> dict:

        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "college": self.college
        }

    @classmethod
    def from_dict(cls, data: dict):

        return cls(
            data["id"],
            data["name"],
            data["email"],
            data["phone"],
            data.get("college", "")
        )


# ====================================================
# DATA STORE
# ====================================================

class DataStore:
    """Handles all data storage and retrieval"""

    def __init__(self, data_dir: str = "data"):

        self.data_dir = data_dir

        self.events: List[Event] = []
        self.venues: List[Venue] = []
        self.resources: List[Resource] = []
        self.attendees: List[Attendee] = []

        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        self.load_all()

    def load_all(self):
        """Load all data from JSON files"""

        self.events = self._load_data("events.json", Event)
        self.venues = self._load_data("venues.json", Venue)
        self.resources = self._load_data("resources.json", Resource)
        self.attendees = self._load_data("attendees.json", Attendee)

    def _load_data(self, filename: str, data_class):

        filepath = os.path.join(self.data_dir, filename)

        if os.path.exists(filepath):

            try:
                with open(filepath, "r", encoding="utf-8") as file:

                    data_list = json.load(file)

                    return [
                        data_class.from_dict(item)
                        for item in data_list
                    ]

            except (json.JSONDecodeError, KeyError, TypeError):
                return []

        return []

    def _save_data(self, filename: str, data_list: List):

        filepath = os.path.join(self.data_dir, filename)

        try:

            with open(filepath, "w", encoding="utf-8") as file:

                json.dump(
                    [item.to_dict() for item in data_list],
                    file,
                    indent=4
                )

        except (OSError, TypeError):
            print(f"⚠️ Unable to save {filename}")

    def save_all(self):
        """Save all data to JSON files"""

        self._save_data("events.json", self.events)
        self._save_data("venues.json", self.venues)
        self._save_data("resources.json", self.resources)
        self._save_data("attendees.json", self.attendees)

    def get_next_id(self, data_list: List) -> int:
        """Get next available ID"""

        if not data_list:
            return 1

        return max(item.id for item in data_list) + 1

    def find_event(self, event_id: int) -> Optional[Event]:

        for event in self.events:

            if event.id == event_id:
                return event

        return None

    def find_venue(self, venue_id: int) -> Optional[Venue]:

        for venue in self.venues:

            if venue.id == venue_id:
                return venue

        return None

    def find_resource(self, resource_id: int) -> Optional[Resource]:

        for resource in self.resources:

            if resource.id == resource_id:
                return resource

        return None

    def find_resource_by_name(self, name: str) -> Optional[Resource]:

        for resource in self.resources:

            if resource.name.lower() == name.lower():
                return resource

        return None

    def find_attendee(self, attendee_id: int) -> Optional[Attendee]:

        for attendee in self.attendees:

            if attendee.id == attendee_id:
                return attendee

        return None


# ====================================================
# EVENT MANAGEMENT
# ====================================================

class EventManager:
    """Handles event-related operations"""

    def __init__(self, data_store: DataStore):

        self.db = data_store

    def create_event(self):

        print("\n" + "=" * 50)
        print("   CREATE NEW EVENT")
        print("=" * 50)

        name = input("Event Name : ").strip()

        if not name:

            print("❌ Event name cannot be empty.")
            return

        print("\nEvent Types:")

        event_types = [
            "Conference",
            "Workshop",
            "Seminar",
            "Hackathon",
            "Cultural Fest",
            "Sports Meet",
            "Wedding",
            "Other"
        ]

        for i, event_type in enumerate(event_types, 1):

            print(f"  {i}. {event_type}")

        try:

            type_choice = int(
                input("Select Event Type (1-8): ")
            )

            if 1 <= type_choice <= 8:
                event_type = event_types[type_choice - 1]
            else:
                event_type = "Other"

        except ValueError:

            event_type = "Other"

        date = input("Date (DD/MM/YYYY) : ").strip()

        time = input("Time (HH:MM AM/PM) : ").strip()

        try:

            budget = float(
                input("Budget (₹) : ").strip() or "0"
            )

            if budget < 0:
                print("❌ Budget cannot be negative.")
                return

        except ValueError:

            print("❌ Invalid budget.")
            return

        description = input(
            "Description (optional) : "
        ).strip()

        try:

            datetime.strptime(
                date,
                "%d/%m/%Y"
            )

        except ValueError:

            print(
                "⚠️ Invalid date format. "
                "Please use DD/MM/YYYY"
            )

            return

        event_id = self.db.get_next_id(
            self.db.events
        )

        event = Event(
            event_id,
            name,
            event_type,
            date,
            time,
            budget,
            description
        )

        self.db.events.append(event)

        self.db.save_all()

        print(
            f"✅ Event '{name}' Created Successfully! "
            f"(ID: {event_id})"
        )

    def view_events(self):

        print("\n" + "=" * 50)
        print("   EVENT LIST")
        print("=" * 50)

        if not self.db.events:

            print("📭 No Events Available.")
            return

        for event in self.db.events:

            print(f"""
┌─────────────────────────────────────────────
│ ID          : {event.id}
│ Name        : {event.name}
│ Type        : {event.event_type}
│ Date        : {event.date}
│ Time        : {event.time}
│ Venue       : {event.venue}
│ Status      : {event.status}
│ Budget      : ₹{event.budget:,.2f}
│ Attendees   : {len(event.attendees)}
│ Resources   : {len(event.resources)}
└─────────────────────────────────────────────
""")

    def update_event(self):

        self.view_events()

        if not self.db.events:
            return

        try:

            event_id = int(
                input("\nEnter Event ID to Update: ")
            )

        except ValueError:

            print("❌ Invalid Input")
            return

        event = self.db.find_event(event_id)

        if event is None:

            print("❌ Event Not Found")
            return

        print("\n--- Update Event Details ---")

        print(f"Current Name: {event.name}")

        new_name = input(
            "New Name (press Enter to keep): "
        ).strip()

        if new_name:
            event.name = new_name

        print(f"Current Type: {event.event_type}")

        new_type = input(
            "New Type (press Enter to keep): "
        ).strip()

        if new_type:
            event.event_type = new_type

        print(f"Current Date: {event.date}")

        new_date = input(
            "New Date (DD/MM/YYYY, press Enter to keep): "
        ).strip()

        if new_date:

            try:

                datetime.strptime(
                    new_date,
                    "%d/%m/%Y"
                )

                event.date = new_date

            except ValueError:

                print("⚠️ Invalid date. Keeping old date.")

        print(f"Current Time: {event.time}")

        new_time = input(
            "New Time (press Enter to keep): "
        ).strip()

        if new_time:
            event.time = new_time

        print(
            f"Current Budget: ₹{event.budget:,.2f}"
        )

        new_budget = input(
            "New Budget (press Enter to keep): "
        ).strip()

        if new_budget:

            try:

                budget = float(new_budget)

                if budget >= 0:
                    event.budget = budget
                else:
                    print("⚠️ Budget cannot be negative.")

            except ValueError:

                print("⚠️ Invalid budget.")

        print(f"Current Status: {event.status}")

        print(
            "Available Statuses: "
            "Planning, In Progress, Completed, Cancelled"
        )

        new_status = input(
            "New Status (press Enter to keep): "
        ).strip()

        if new_status in [
            "Planning",
            "In Progress",
            "Completed",
            "Cancelled"
        ]:

            event.status = new_status

        self.db.save_all()

        print("✅ Event Updated Successfully!")

    def delete_event(self):

        self.view_events()

        if not self.db.events:
            return

        try:

            event_id = int(
                input("\nEnter Event ID to Delete: ")
            )

        except ValueError:

            print("❌ Invalid Input")
            return

        event = self.db.find_event(event_id)

        if event:

            confirm = input(
                f"Are you sure you want to delete "
                f"'{event.name}'? (y/n): "
            )

            if confirm.lower() == "y":

                self.db.events.remove(event)

                self.db.save_all()

                print(
                    "✅ Event Deleted Successfully!"
                )

            else:

                print("❌ Deletion cancelled.")

        else:

            print("❌ Event Not Found")

    def get_event_details(self):

        self.view_events()

        if not self.db.events:
            return

        try:

            event_id = int(
                input("\nEnter Event ID: ")
            )

        except ValueError:

            print("❌ Invalid Input")
            return

        event = self.db.find_event(event_id)

        if event is None:

            print("❌ Event Not Found")
            return

        print("\n" + "=" * 50)
        print(
            f"   EVENT DETAILS - {event.name}"
        )
        print("=" * 50)

        print(f"""
ID          : {event.id}
Name        : {event.name}
Type        : {event.event_type}
Date        : {event.date}
Time        : {event.time}
Venue       : {event.venue}
Status      : {event.status}
Budget      : ₹{event.budget:,.2f}
Description : {event.description or 'N/A'}
Created At  : {event.created_at}
""")

        print("--- Resources ---")

        if not event.resources:

            print("  No resources allocated.")

        else:

            for resource in event.resources:

                print(
                    f"  • {resource['name']} - "
                    f"{resource['quantity']} units"
                )

        print("\n--- Attendees ---")

        if not event.attendees:

            print("  No attendees registered.")

        else:

            for attendee in event.attendees:

                print(
                    f"  • {attendee['name']} "
                    f"<{attendee['email']}>"
                )


# ====================================================
# VENUE MANAGEMENT
# ====================================================

class VenueManager:
    """Handles venue-related operations"""

    def __init__(self, data_store: DataStore):

        self.db = data_store

    def add_venue(self):

        print("\n" + "=" * 50)
        print("   ADD NEW VENUE")
        print("=" * 50)

        name = input("Venue Name : ").strip()

        if not name:

            print("❌ Venue name cannot be empty.")
            return

        for venue in self.db.venues:

            if venue.name.lower() == name.lower():

                print("⚠️ Venue already exists.")
                return

        try:

            capacity = int(
                input("Capacity : ")
            )

            if capacity <= 0:

                print("❌ Capacity must be greater than zero.")
                return

        except ValueError:

            print("❌ Invalid capacity.")
            return

        location = input(
            "Location : "
        ).strip()

        facilities = []

        print(
            "\nEnter facilities "
            "(one per line, type 'done' to finish):"
        )

        while True:

            facility = input(
                "Facility: "
            ).strip()

            if facility.lower() == "done":
                break

            if facility:
                facilities.append(facility)

        venue_id = self.db.get_next_id(
            self.db.venues
        )

        venue = Venue(
            venue_id,
            name,
            capacity,
            location,
            facilities
        )

        self.db.venues.append(venue)

        self.db.save_all()

        print(
            f"✅ Venue '{name}' Added Successfully! "
            f"(ID: {venue_id})"
        )

    def view_venues(self):

        print("\n" + "=" * 50)
        print("   VENUE LIST")
        print("=" * 50)

        if not self.db.venues:

            print("📭 No Venues Available.")
            return

        for venue in self.db.venues:

            print(f"""
┌─────────────────────────────────────────────
│ ID          : {venue.id}
│ Name        : {venue.name}
│ Capacity    : {venue.capacity}
│ Location    : {venue.location}
│ Facilities  : {', '.join(venue.facilities) if venue.facilities else 'None'}
│ Available   : {'✅ Yes' if venue.is_available else '❌ No'}
└─────────────────────────────────────────────
""")

    def assign_venue(self):

        print("\n--- Available Events ---")

        if not self.db.events:

            print(
                "❌ No events available. "
                "Create an event first."
            )

            return

        for event in self.db.events:

            print(
                f"{event.id}. {event.name} "
                f"(Status: {event.status})"
            )

        try:

            event_id = int(
                input("\nSelect Event ID: ")
            )

        except ValueError:

            print("❌ Invalid Input")
            return

        event = self.db.find_event(event_id)

        if event is None:

            print("❌ Event Not Found")
            return

        print("\n--- Available Venues ---")

        available_venues = [
            venue
            for venue in self.db.venues
            if venue.is_available
        ]

        if not available_venues:

            print("❌ No available venues.")
            return

        for venue in available_venues:

            print(
                f"{venue.id}. {venue.name} "
                f"(Capacity: {venue.capacity})"
            )

        try:

            venue_id = int(
                input("Select Venue ID: ")
            )

        except ValueError:

            print("❌ Invalid Input")
            return

        venue = self.db.find_venue(venue_id)

        if venue is None:

            print("❌ Venue Not Found")
            return

        if not venue.is_available:

            print("❌ Venue is not available.")
            return

        # Scheduling conflict detection
        for other_event in self.db.events:

            if other_event.id == event.id:
                continue

            if (
                other_event.venue == venue.name
                and other_event.date == event.date
                and other_event.time == event.time
                and other_event.status != "Cancelled"
            ):

                print(
                    f"⚠️ Scheduling Conflict! "
                    f"Venue already booked for "
                    f"'{other_event.name}' "
                    f"on {event.date} at {event.time}."
                )

                return

        event.venue = venue.name

        venue.is_available = False

        event.status = "In Progress"

        self.db.save_all()

        print(
            f"✅ Venue '{venue.name}' "
            f"assigned to '{event.name}'!"
        )

    def release_venue(self):

        self.view_venues()

        if not self.db.venues:
            return

        try:

            venue_id = int(
                input("\nEnter Venue ID to Release: ")
            )

        except ValueError:

            print("❌ Invalid Input")
            return

        venue = self.db.find_venue(venue_id)

        if venue is None:

            print("❌ Venue Not Found")
            return

        if venue.is_available:

            print("⚠️ Venue is already available.")
            return

        venue.is_available = True

        for event in self.db.events:

            if event.venue == venue.name:

                event.venue = "Not Assigned"

        self.db.save_all()

        print(
            f"✅ Venue '{venue.name}' released!"
        )


# ====================================================
# RESOURCE MANAGEMENT
# ====================================================

class ResourceManager:
    """Handles resource-related operations"""

    def __init__(self, data_store: DataStore):

        self.db = data_store

    def add_resource(self):

        print("\n" + "=" * 50)
        print("   ADD NEW RESOURCE")
        print("=" * 50)

        name = input("Resource Name : ").strip()

        if not name:

            print("❌ Resource name cannot be empty.")
            return

        try:

            quantity = int(
                input("Quantity : ")
            )

            if quantity <= 0:

                print(
                    "❌ Quantity must be greater than zero."
                )

                return

        except ValueError:

            print("❌ Invalid quantity.")
            return

        print("\nCategories:")

        categories = [
            "Equipment",
            "Furniture",
            "Electronics",
            "Staff",
            "Other"
        ]

        for i, category in enumerate(
            categories,
            1
        ):

            print(
                f"  {i}. {category}"
            )

        try:

            choice = int(
                input("Select Category (1-5): ")
            )

            if 1 <= choice <= 5:
                category = categories[choice - 1]
            else:
                category = "Other"

        except ValueError:

            category = "Other"

        description = input(
            "Description (optional) : "
        ).strip()

        resource_id = self.db.get_next_id(
            self.db.resources
        )

        resource = Resource(
            resource_id,
            name,
            quantity,
            category,
            description
        )

        self.db.resources.append(resource)

        self.db.save_all()

        print(
            f"✅ Resource '{name}' "
            f"Added Successfully! "
            f"(ID: {resource_id})"
        )

    def view_resources(self):

        print("\n" + "=" * 50)
        print("   RESOURCE LIST")
        print("=" * 50)

        if not self.db.resources:

            print("📭 No Resources Available.")
            return

        for resource in self.db.resources:

            print(f"""
┌─────────────────────────────────────────────
│ ID          : {resource.id}
│ Name        : {resource.name}
│ Category    : {resource.category}
│ Total       : {resource.quantity}
│ Reserved    : {resource.reserved}
│ Available   : {resource.available}
└─────────────────────────────────────────────
""")

    def allocate_resource(self):

        print("\n--- Available Events ---")

        if not self.db.events:

            print("❌ No events available.")
            return

        available_events = [
            event
            for event in self.db.events
            if event.status not in [
                "Completed",
                "Cancelled"
            ]
        ]

        if not available_events:

            print("❌ No events available for allocation.")
            return

        for event in available_events:

            print(
                f"{event.id}. {event.name} "
                f"(Status: {event.status})"
            )

        try:

            event_id = int(
                input("\nSelect Event ID: ")
            )

        except ValueError:

            print("❌ Invalid Input")
            return

        event = self.db.find_event(event_id)

        if event is None:

            print("❌ Event Not Found")
            return

        self.view_resources()

        if not self.db.resources:
            return

        try:

            resource_id = int(
                input("\nSelect Resource ID: ")
            )

        except ValueError:

            print("❌ Invalid Input")
            return

        resource = self.db.find_resource(
            resource_id
        )

        if resource is None:

            print("❌ Resource Not Found")
            return

        if resource.available <= 0:

            print(
                "❌ Not enough resources available."
            )

            return

        try:

            quantity = int(
                input(
                    f"Quantity "
                    f"(Available: {resource.available}): "
                )
            )

        except ValueError:

            print("❌ Invalid Quantity")
            return

        if quantity <= 0:

            print("❌ Quantity must be greater than zero.")
            return

        if quantity > resource.available:

            print(
                f"❌ Not enough resources. "
                f"Only {resource.available} available."
            )

            return

        resource.reserved += quantity

        event.resources.append(
            {
                "resource_id": resource.id,
                "name": resource.name,
                "quantity": quantity
            }
        )

        self.db.save_all()

        print(
            f"✅ {quantity} '{resource.name}' "
            f"allocated to '{event.name}'!"
        )

    def release_resource(self):

        self.view_resources()

        if not self.db.resources:
            return

        try:

            resource_id = int(
                input(
                    "\nEnter Resource ID to Release: "
                )
            )

        except ValueError:

            print("❌ Invalid Input")
            return

        resource = self.db.find_resource(
            resource_id
        )

        if resource is None:

            print("❌ Resource Not Found")
            return

        if resource.reserved <= 0:

            print(
                "⚠️ No resources reserved to release."
            )

            return

        try:

            quantity = int(
                input(
                    f"Quantity to release "
                    f"(Reserved: {resource.reserved}): "
                )
            )

        except ValueError:

            print("❌ Invalid Quantity")
            return

        if quantity <= 0:

            print("❌ Quantity must be greater than zero.")
            return

        if quantity > resource.reserved:

            print(
                f"❌ Cannot release more than reserved. "
                f"Only {resource.reserved} reserved."
            )

            return

        remaining = quantity

        # Release from events
        for event in self.db.events:

            for allocation in list(event.resources):

                if (
                    allocation.get("resource_id")
                    == resource.id
                ):

                    release_amount = min(
                        allocation["quantity"],
                        remaining
                    )

                    allocation["quantity"] -= (
                        release_amount
                    )

                    remaining -= release_amount

                    if allocation["quantity"] <= 0:

                        event.resources.remove(
                            allocation
                        )

                    if remaining <= 0:
                        break

            if remaining <= 0:
                break

        resource.reserved -= quantity

        self.db.save_all()

        print(
            f"✅ {quantity} '{resource.name}' "
            f"released!"
        )


# ====================================================
# ATTENDEE MANAGEMENT
# ====================================================

class AttendeeManager:
    """Handles attendee-related operations"""

    def __init__(self, data_store: DataStore):

        self.db = data_store

    def register_attendee(self):

        print("\n--- Available Events ---")

        if not self.db.events:

            print("❌ No events available.")
            return

        available_events = [
            event
            for event in self.db.events
            if event.status not in [
                "Completed",
                "Cancelled"
            ]
        ]

        if not available_events:

            print("❌ No events available for registration.")
            return

        for event in available_events:

            print(
                f"{event.id}. {event.name} "
                f"(Date: {event.date})"
            )

        try:

            event_id = int(
                input("\nSelect Event ID: ")
            )

        except ValueError:

            print("❌ Invalid Input")
            return

        event = self.db.find_event(event_id)

        if event is None:

            print("❌ Event Not Found")
            return

        print("\n--- Attendee Details ---")

        name = input(
            "Full Name : "
        ).strip()

        if not name:

            print("❌ Name cannot be empty.")
            return

        email = input(
            "Email : "
        ).strip()

        if not email:

            print("❌ Email cannot be empty.")
            return

        phone = input(
            "Phone Number : "
        ).strip()

        college = input(
            "College/Organization : "
        ).strip()

        # Check duplicate email for this event
        for attendee in event.attendees:

            if attendee["email"].lower() == email.lower():

                print(
                    "⚠️ This attendee is already "
                    "registered for this event."
                )

                return

        attendee_id = self.db.get_next_id(
            self.db.attendees
        )

        attendee = Attendee(
            attendee_id,
            name,
            email,
            phone,
            college
        )

        self.db.attendees.append(attendee)

        event.attendees.append(
            {
                "id": attendee_id,
                "name": name,
                "email": email
            }
        )

        self.db.save_all()

        print(
            f"✅ {name} registered successfully "
            f"for '{event.name}'!"
        )

        print(
            f"   Registration ID: {attendee_id}"
        )

    def view_attendees(self):

        print("\n" + "=" * 50)
        print("   ATTENDEE LIST")
        print("=" * 50)

        if not self.db.attendees:

            print("📭 No Attendees Registered.")
            return

        for attendee in self.db.attendees:

            print(f"""
┌─────────────────────────────────────────────
│ ID          : {attendee.id}
│ Name        : {attendee.name}
│ Email       : {attendee.email}
│ Phone       : {attendee.phone}
│ College     : {attendee.college or 'N/A'}
└─────────────────────────────────────────────
""")


# ====================================================
# REPORT MANAGEMENT
# ====================================================

class ReportManager:
    """Handles report generation"""

    def __init__(self, data_store: DataStore):

        self.db = data_store

    def generate_event_report(self):

        print("\n" + "=" * 60)
        print("   📊 EVENT REPORT")
        print("=" * 60)

        if not self.db.events:

            print("📭 No Events Available.")
            return

        total_events = len(
            self.db.events
        )

        completed = sum(
            1
            for event in self.db.events
            if event.status == "Completed"
        )

        in_progress = sum(
            1
            for event in self.db.events
            if event.status == "In Progress"
        )

        planning = sum(
            1
            for event in self.db.events
            if event.status == "Planning"
        )

        cancelled = sum(
            1
            for event in self.db.events
            if event.status == "Cancelled"
        )

        total_budget = sum(
            event.budget
            for event in self.db.events
        )

        total_attendees = sum(
            len(event.attendees)
            for event in self.db.events
        )

        print(f"""
📋 SUMMARY
├─ Total Events      : {total_events}
├─ Completed         : {completed}
├─ In Progress       : {in_progress}
├─ Planning          : {planning}
├─ Cancelled         : {cancelled}
├─ Total Budget      : ₹{total_budget:,.2f}
└─ Total Attendees   : {total_attendees}
""")

        print("\n--- Event Details ---")

        for event in self.db.events:

            print(f"""
📌 {event.name} (ID: {event.id})
   ├─ Type        : {event.event_type}
   ├─ Date        : {event.date}
   ├─ Time        : {event.time}
   ├─ Venue       : {event.venue}
   ├─ Status      : {event.status}
   ├─ Budget      : ₹{event.budget:,.2f}
   └─ Attendees   : {len(event.attendees)}
""")

    def generate_venue_report(self):

        print("\n" + "=" * 60)
        print("   🏢 VENUE UTILIZATION REPORT")
        print("=" * 60)

        if not self.db.venues:

            print("📭 No Venues Available.")
            return

        for venue in self.db.venues:

            event_count = sum(
                1
                for event in self.db.events
                if event.venue == venue.name
            )

            usage_percentage = (
                event_count
                / len(self.db.events)
                * 100
                if self.db.events
                else 0
            )

            print(f"""
🏛️  {venue.name}
   ├─ ID          : {venue.id}
   ├─ Capacity    : {venue.capacity}
   ├─ Location    : {venue.location}
   ├─ Available   : {'✅ Yes' if venue.is_available else '❌ No'}
   ├─ Events Held : {event_count}
   └─ Usage       : {usage_percentage:.1f}%
""")

    def generate_resource_report(self):

        print("\n" + "=" * 60)
        print("   🔧 RESOURCE UTILIZATION REPORT")
        print("=" * 60)

        if not self.db.resources:

            print("📭 No Resources Available.")
            return

        for resource in self.db.resources:

            usage_percentage = (
                resource.reserved
                / resource.quantity
                * 100
                if resource.quantity > 0
                else 0
            )

            print(f"""
🔧 {resource.name}
   ├─ ID          : {resource.id}
   ├─ Category    : {resource.category}
   ├─ Total       : {resource.quantity}
   ├─ Reserved    : {resource.reserved}
   ├─ Available   : {resource.available}
   └─ Utilization : {usage_percentage:.1f}%
""")

    def generate_attendee_report(self):

        print("\n" + "=" * 60)
        print("   👤 ATTENDEE REPORT")
        print("=" * 60)

        if not self.db.attendees:

            print("📭 No Attendees Registered.")
            return

        print(
            f"Total Attendees: "
            f"{len(self.db.attendees)}\n"
        )

        college_stats = {}

        for attendee in self.db.attendees:

            college = (
                attendee.college
                or "Unknown"
            )

            college_stats[college] = (
                college_stats.get(college, 0)
                + 1
            )

        print(
            "📊 Attendees by Organization:"
        )

        for college, count in sorted(
            college_stats.items(),
            key=lambda item: item[1],
            reverse=True
        ):

            print(
                f"  • {college}: {count}"
            )


# ====================================================
# MAIN MENU
# ====================================================

class MainMenu:
    """Main application menu"""

    def __init__(self):

        self.db = DataStore()

        self.event_manager = EventManager(
            self.db
        )

        self.venue_manager = VenueManager(
            self.db
        )

        self.resource_manager = ResourceManager(
            self.db
        )

        self.attendee_manager = AttendeeManager(
            self.db
        )

        self.report_manager = ReportManager(
            self.db
        )

    def display_menu(self):

        print("\n" + "=" * 60)
        print(
            "   🌐 EVENTSPHERE - "
            "EVENT MANAGEMENT SYSTEM"
        )
        print("=" * 60)

        print("""
┌──────────────────────────────────────────────────┐
│  📋 EVENT MANAGEMENT                              │
│    1. Create Event                                │
│    2. View Events                                 │
│    3. Update Event                                │
│    4. Delete Event                                │
│    5. Event Details                               │
├──────────────────────────────────────────────────┤
│  🏢 VENUE MANAGEMENT                              │
│    6. Add Venue                                   │
│    7. View Venues                                 │
│    8. Assign Venue to Event                       │
│    9. Release Venue                               │
├──────────────────────────────────────────────────┤
│  🔧 RESOURCE MANAGEMENT                           │
│    10. Add Resource                               │
│    11. View Resources                             │
│    12. Allocate Resource to Event                 │
│    13. Release Resource                           │
├──────────────────────────────────────────────────┤
│  👤 ATTENDEE MANAGEMENT                           │
│    14. Register Attendee                          │
│    15. View Attendees                             │
├──────────────────────────────────────────────────┤
│  📊 REPORTS                                       │
│    16. Event Report                               │
│    17. Venue Report                               │
│    18. Resource Report                            │
│    19. Attendee Report                            │
├──────────────────────────────────────────────────┤
│  💾 DATA MANAGEMENT                               │
│    20. Save Data                                  │
│    21. Load Data                                  │
│    22. Clear All Data                             │
├──────────────────────────────────────────────────┤
│    23. Exit                                       │
└──────────────────────────────────────────────────┘
""")

    def run(self):

        while True:

            self.display_menu()

            try:

                choice = input(
                    "Enter your choice (1-23): "
                ).strip()

                if choice == "1":

                    self.event_manager.create_event()

                elif choice == "2":

                    self.event_manager.view_events()

                elif choice == "3":

                    self.event_manager.update_event()

                elif choice == "4":

                    self.event_manager.delete_event()

                elif choice == "5":

                    self.event_manager.get_event_details()

                elif choice == "6":

                    self.venue_manager.add_venue()

                elif choice == "7":

                    self.venue_manager.view_venues()

                elif choice == "8":

                    self.venue_manager.assign_venue()

                elif choice == "9":

                    self.venue_manager.release_venue()

                elif choice == "10":

                    self.resource_manager.add_resource()

                elif choice == "11":

                    self.resource_manager.view_resources()

                elif choice == "12":

                    self.resource_manager.allocate_resource()

                elif choice == "13":

                    self.resource_manager.release_resource()

                elif choice == "14":

                    self.attendee_manager.register_attendee()

                elif choice == "15":

                    self.attendee_manager.view_attendees()

                elif choice == "16":

                    self.report_manager.generate_event_report()

                elif choice == "17":

                    self.report_manager.generate_venue_report()

                elif choice == "18":

                    self.report_manager.generate_resource_report()

                elif choice == "19":

                    self.report_manager.generate_attendee_report()

                elif choice == "20":

                    self.db.save_all()

                    print(
                        "✅ Data saved successfully!"
                    )

                elif choice == "21":

                    self.db.load_all()

                    print(
                        "✅ Data loaded successfully!"
                    )

                elif choice == "22":

                    confirm = input(
                        "⚠️ Are you sure you want "
                        "to clear all data? (yes/no): "
                    )

                    if confirm.lower() == "yes":

                        self.db.events.clear()
                        self.db.venues.clear()
                        self.db.resources.clear()
                        self.db.attendees.clear()

                        self.db.save_all()

                        print(
                            "✅ All data cleared successfully!"
                        )

                    else:

                        print(
                            "❌ Clear operation cancelled."
                        )

                elif choice == "23":

                    print("\n" + "=" * 60)
                    print(
                        "   Thank you for using EventSphere!"
                    )
                    print("=" * 60)

                    break

                else:

                    print(
                        "❌ Invalid Choice! "
                        "Please select a number from 1 to 23."
                    )

            except KeyboardInterrupt:

                print(
                    "\n\n⚠️ Program interrupted."
                )

                break

            except Exception as error:

                print(
                    f"\n❌ An unexpected error occurred: "
                    f"{error}"
                )


# ====================================================
# PROGRAM START
# ====================================================

if __name__ == "__main__":

    app = MainMenu()

    app.run()