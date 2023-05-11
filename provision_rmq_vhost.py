import requests


def provision_vhost(
    host: str,
    port: str,
    admin_username: str,
    admin_password: str,
    vhost_name: str,
    username: str,
    password: str,
    port_forwarded: bool = False,
):
    print("Creating vhost...")
    base_url = f"https://{host}"

    if port_forwarded:
        base_url = f"http://0.0.0.0"
    else:
        base_url = f"https://{host}"

    r = requests.put(
        f"{base_url}:{port}/api/vhosts/{vhost_name}",
        auth=(admin_username, admin_password),
    )

    r.raise_for_status()

    # now we create the user
    r = requests.put(
        f"{base_url}:{port}/api/users/{username}",
        auth=(admin_username, admin_password),
        json={"password": password, "tags": ""},  # tags cannot be None
    )
    print(r)

    r.raise_for_status()

    # now give user permission
    r = requests.put(
        f"{base_url}:{port}/api/permissions/{vhost_name}/{username}",
        auth=(admin_username, admin_password),
        json={"configure": ".*", "write": ".*", "read": ".*"},
    )

    r.raise_for_status()
    print("Successfully created vhost")


if __name__ == "__main__":
    provision_vhost(
        host="localhost",
        port="15672",
        admin_username="admin",
        admin_password="adminpassword",
        vhost_name="my v host",
        username="vhost user",
        password="vhost password",
        port_forwarded=False,
    )