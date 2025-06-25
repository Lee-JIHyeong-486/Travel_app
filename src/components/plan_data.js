class Location {
  constructor(latitude, longitude) {
    this.latitude = latitude;
    this.longitude = longitude;
  }
}

class Visiting {
  constructor(name, location, concept) {
    this.name = name;
    this.location = location; // instance of Location
    this.concept = concept;
  }
}

class DayPlan {
  constructor(date, place_to_visit = []) {
    this.date = date;
    this.place_to_visit = place_to_visit; // array of Visiting instances
  }
}

class TravelPlan {
  constructor(dayplan = []) {
    this.dayplan = dayplan; // array of DayPlan instances
  }
}
