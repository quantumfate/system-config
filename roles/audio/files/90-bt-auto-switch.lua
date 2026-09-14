log = Log.open_topic("s-bt-auto-switch")
nutils = require("node-utils")

local function set_default_sink(source, node_name)
  local om = source:call("get-object-manager", "metadata")
  local metadata = om:lookup({
    Constraint({ "metadata.name", "=", "default" }),
  })
  if not metadata then
    log:warning("default metadata not found")
    return
  end
  metadata:set(0, "default.audio.sink", "Spa:String:JSON", Json.Object({ name = node_name }):to_string())
  log:info("default audio sink set to " .. node_name)
end

local function find_best_fallback_sink(source, exclude_name)
  local si_om = source:call("get-object-manager", "session-item")
  local best_name, best_prio = nil, -1

  for linkable in
    si_om:iterate({
      type = "SiLinkable",
      Constraint({ "media.class", "c", "Audio/Sink", "Audio/Duplex" }),
    })
  do
    local node = linkable:get_associated_proxy("node")
    if node and node.properties then
      local name = node.properties["node.name"]
      if name and name ~= exclude_name then
        local prio = nutils.get_session_priority(node.properties)
        if prio and prio > best_prio then
          best_prio = prio
          best_name = name
        end
      end
    end
  end

  return best_name
end

SimpleEventHook({
  name = "bt-auto-switch/on-connect",
  interests = {
    EventInterest({
      Constraint({ "event.type", "=", "node-added" }),
      Constraint({ "node.name", "#", "bluez_output.*" }),
    }),
  },
  execute = function(event)
    local node = event:get_subject()
    local source = event:get_source()
    local node_name = node.properties["node.name"]
    log:info(node, "bluetooth audio connected: " .. node_name)
    set_default_sink(source, node_name)
  end,
}):register()

SimpleEventHook({
  name = "bt-auto-switch/on-disconnect",
  interests = {
    EventInterest({
      Constraint({ "event.type", "=", "node-removed" }),
      Constraint({ "node.name", "#", "bluez_output.*" }),
    }),
  },
  execute = function(event)
    local node = event:get_subject()
    local source = event:get_source()
    local node_name = node.properties["node.name"]
    log:info(node, "bluetooth audio disconnected: " .. node_name)

    local si_om = source:call("get-object-manager", "session-item")
    for linkable in
      si_om:iterate({
        type = "SiLinkable",
        Constraint({ "media.class", "c", "Audio/Sink" }),
      })
    do
      local n = linkable:get_associated_proxy("node")
      if n and n.properties then
        local name = n.properties["node.name"]
        if name and name ~= node_name and name:match("^bluez_output") then
          log:info("another BT sink still active (" .. name .. "), keeping current default")
          return
        end
      end
    end

    local fallback = find_best_fallback_sink(source, node_name)
    if fallback then
      set_default_sink(source, fallback)
    else
      log:warning("no fallback sink available")
    end
  end,
}):register()
