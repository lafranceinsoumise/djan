-- set key
--
--

local set = KEYS[1]
local key = ARGV[1]

--local ERROR_RATE = 0.001
--local EXPANSION = 4
--local INITIAL_CAPACITY = 1000
local EXPIRATION = 3600 * 24 * 2  -- 2 jours
local result = 1 - redis.call('SISMEMBER', set, key)

if result then
    -- key is not in the set, we need to add it
    redis.call('SADD', set, key)
end

-- extend the expiration time
redis.call('EXPIRE', set, EXPIRATION)

return result