/* 
    Data format for user data input

    - location              : city(currently set as jeju, but if get_pois from map api implemented, can be selected from multiple cities)
    - duration              : duration of trip
    - companions            : has to be number only(check https://hianna.tistory.com/413)
    - concept               :
    - extra_request         : passed to LLM for more user customized travel plan
    - kwargs
        - filter            : for future extension(for user feedback, if llm determines that selected pois is not appropriate, then get new filter, otherwise use prev filter)
        - prev_map_data     : used in user feedback, if user wants to replace part of plan, then use this plan to re-planning
        - poi_file_loc      : used to retreive poi list
*/
export class UserData {
  constructor() {
    this.location = "";
    this.duration = { start: "", end: "" };
    this.companions = "";
    this.concept = 0;
    this.extra_request = "";
    this.kwargs = { filter: null, prev_map_data: null, poi_file_loc: null };
  }

  toJSON() {
    return {
      location: this.location,
      duration: this.duration,
      companions: this.companions,
      concept: this.concept,
      extra_request: this.extra_request,
      kwargs: this.kwargs,
    };
  }
}