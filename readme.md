1. To test this server, first you have to build the required environment  
   - **Strongly recommended**: use a conda virtual environment  
   - To install dependencies, run:

   ```bash
   pip install -r requirements.txt
   ```

2. Move to the `travel_planner` folder and run:

   ```bash
   python BackEnd/run.py
   ```

   - This will start the backend server, accessible through port `3000`

3. Use Postman to test this backend server  
   - Send a `POST` request to:
     - `http://localhost:3000/api/route_optim`
     - or `http://localhost:3000/api/get_pois`  
   - In the request body, select **raw** and choose **JSON** format  
   - Example JSON payload:

   ```json
   {
     "location": "Seoul",
     "duration": {
       "start": "2025-06-01",
       "end": "2025-06-07"
     },
     "companions": "4",
     "concept": "foodie adventure",
     "extra_request": "include hidden cafes",
     "kwargs": {
       "filter": {
         "category": "cafe",
         "rating": "4+"
       },
       "prev_map_data": null,
       "poi_file_loc": "example.csv"
     }
   }
   ```
