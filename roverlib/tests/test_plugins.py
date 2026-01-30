import importlib.metadata

eps = importlib.metadata.entry_points(group="rover.camera")
print(eps)

for ep in eps:
    print(ep.name, "→", ep.load())
