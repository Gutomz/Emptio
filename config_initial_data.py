import argparse
import json
import requests as http

token = ""
admin_token = ""
isAdmin = False

products_ids = {}
active_purchase = None

register_url = "/users"
create_product_url = "/products"

def get_authenticated_headers():
  return { 
    "Authorization": "Bearer {}".format(token if not isAdmin else admin_token),
    "Content-Type": "application/json"
  }

def get_full_url(route):
  return "http://{}/api{}".format(url, route);

def get_product_key(product):
  return "[{}] [{}] [{}]".format(product["name"], product["brand"], product["variation"])

def post(route, data):
  full_url = get_full_url(route)
  headers = get_authenticated_headers()
  return http.post(full_url, data=json.dumps(data), headers=headers)

def put(route, data):
  full_url = get_full_url(route)
  headers = get_authenticated_headers()
  return http.put(full_url, data=json.dumps(data), headers=headers)

def patch(route, data):
  full_url = get_full_url(route)
  headers = get_authenticated_headers()
  return http.patch(full_url, data=json.dumps(data), headers=headers)

def create_admin(admin):
  response = post(register_url, admin)
  if response.status_code == 200:
    response_data = response.json()
    global admin_token
    admin_token = response_data["token"]
  
  return

def add_products(products):
  global isAdmin
  isAdmin = True

  for product in products:
    response = post(create_product_url, product)
    if response.status_code == 200:
      products_ids[get_product_key(product)] = response.json()["_id"]

  isAdmin = False
  return

def create_users(users):
  for user in users:
    post(register_url, user)
  return

def run_requests(requests):
  global active_purchase
  global token

  for request in requests:
    type = request["type"]
    method = request["method"]
    route = request["route"]
    body = request["body"]

    if method == "POST":

      if type == "add_item": 
        route = "{}/{}".format(route, active_purchase)
        body["product_id"] = products_ids[body["product_key"]]
      elif type == "share_purchase":
        body["data"]["purchase"] = active_purchase

      response = post(route, body)

      if response.status_code == 200:
        if type == "auth":
          token = response.json()["token"]

        elif type == "new_purchase":
          active_purchase = response.json()["_id"]

    elif method == "PUT":

      if type == "complete_purchase":
        route = "{}/{}".format(route, active_purchase)

      response = put(route, body)

    elif method == "PATCH":

      if type == "connect_market":
        route = "{}/{}/connect".format(route, active_purchase)

      response = patch(route, body)

  return

#------------------------------------------------------------# Start System

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--path', help='Json file path')
parser.add_argument('-u', '--url', help='API url')
args = parser.parse_args()

path = args.path
url = args.url

print("Path: {}".format(path))
print("Url: {}".format(url))


with open(path, encoding='utf-8') as f:
  json_data = json.load(f)

  admin = json_data["admin-user"]
  users = json_data["users"]
  products = json_data["products"]
  requests = json_data["requests"]

  print("Start Initial Data Configuration")

  print("\t• Creating Admin")
  create_admin(admin)

  print("\t• Adding Products")
  add_products(products)

  print("\t• Creating Users")
  create_users(users)

  print("\t• Running Requests")
  run_requests(requests)

print("Done.")
