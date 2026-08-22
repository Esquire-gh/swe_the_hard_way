"""A cache keyed on the wrong thing, and the visitor who finds it.

Caching a page that is the same for everyone is safe. Caching a page that
differs per visitor, under a key that does not include the visitor, hands
one person another person's page. This caches the logged-in home page by
its path alone, and a second visitor is served the first one's private
greeting.

Run it with:  python3 wrong_key.py
"""

by_path = {}          # the cache: path -> rendered page
built = 0


def home_page(user):
    global built
    built += 1
    return f"<h1>Welcome back, {user}</h1><p>Your private messages...</p>"


def handle(path, user):
    # The bug: the key is the path, but the page depends on the user.
    if path not in by_path:
        by_path[path] = home_page(user)
    return by_path[path]


print("Ada signs in and loads /home:")
print("   ", handle("/home", "Ada"))
print("\nGrace signs in and loads /home:")
print("   ", handle("/home", "Grace"))
print(f"\npages actually built: {built}")
print("Grace was served Ada's page: the key forgot who was asking")
