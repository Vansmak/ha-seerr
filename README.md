# Seerr for Home Assistant

Monitor and control your [Jellyseerr](https://github.com/Fallenbagel/jellyseerr) or [Overseerr](https://overseerr.dev) instance from Home Assistant.

## Features

- Monitor requests, issues, and media status
- Request movies and TV shows (including 4K content)
- Update media status without needing request IDs
- Real-time updates via webhooks
- Compatible with both Jellyseerr and Overseerr

## Installation

### HACS (Recommended)
1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the three dots menu → "Custom Repositories"
4. Add this repository URL
5. Category: Integration
6. Click "Install"
7. Restart Home Assistant

### Manual
1. Copy the `seerr` folder to your `custom_components` directory
2. Restart Home Assistant

## Configuration

### Option 1: UI Configuration
1. Go to Settings → Devices & Services
2. Click "Add Integration"
3. Search for "seerr"
4. Follow the configuration flow

### Option 2: YAML Configuration

```yaml
seerr:
  host: YOUR_HOST
  port: 5055  # Optional, default: 5055
  api_key: YOUR_API_KEY
  ssl: false  # Optional, default: false
  verify_ssl: true  # Optional, default: true
  scan_interval: 300  # Optional, default: 300 seconds
```

### API Key Location
1. Open your Jellyseerr/Overseerr web interface
2. Go to Settings → General
3. Copy your API key

[Previous content remains the same until the Services section]

## Services

### `seerr.submit_movie_request`
Request a movie.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `name` | Yes | Movie title to search for |
| `type` | No | `4k` or `standard`. Defaults to `4k` if your seerr user has 4K permissions, otherwise defaults to `standard`. Setting this to `standard` when you have 4K permissions allows you to specifically request the standard version. |

Example:
```yaml
service: seerr.submit_movie_request
data:
  name: "Avatar"
  type: # parameter is optional - will default to 4k if you have permissions # specify type: "standard" only if you specifically want standard quality when you have 4K permissions
```

### `seerr.submit_tv_request`
Request a TV show.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `name` | Yes | TV show title to search for |
| `season` | No | `first`, `latest`, or `all` (default: latest) |
| `type` | No | `4k` or `standard`. Defaults to `4k` if your seerr user has 4K permissions, otherwise defaults to `standard`. Setting this to `standard` when you have 4K permissions allows you to specifically request the standard version. |

[Rest of the document remains the same]
Example:
```yaml
service: seerr.submit_tv_request
data:
  name: "Breaking Bad"
  season: "all"
  type: # parameter is optional - will default to 4k if you have permissions # specify type: "standard" only if you specifically want standard quality when you have 4K permissions
```

### `seerr.update_media_status`
Update media status by title (no request ID needed).

| Parameter | Required | Description |
|-----------|----------|-------------|
| `name` | Yes | Media title to search for |
| `type` | Yes | `movie` or `tv` |
| `new_status` | Yes | `pending`, `approve`, `decline`, or `available` |

Example:
```yaml
service: seerr.update_media_status
data:
  name: "Avatar"
  type: "movie"
  new_status: "approve"
```

## Webhook Setup

Enable real-time updates using webhooks:

1. In Jellyseerr/Overseerr, go to Settings → Notifications → Webhook
2. Enable Agent
3. Set Webhook URL to:
   ```
   {YOUR_HA_URL}/api/webhook/{YOUR_API_KEY}
   ```
   Example: `http://homeassistant.local:8123/api/webhook/abcd1234...`
4. Select notification types:
   - Media Requested
   - Media Approved
   - Media Available
5. Enable "Notifications for Auto-Approved Requests" in global settings
6. Leave payload as default
7. Authorization Header can be left blank

With webhooks enabled, you can increase the `scan_interval` to reduce API calls.

## Sensors

The integration provides several sensors:
- Movie Requests
- TV Show Requests
- Pending Requests
- Total Requests
- Issues

Each sensor includes detailed attributes about the latest request or issue.

## Troubleshooting

1. Check your API key is correct
2. Verify host/port settings
3. Check SSL settings if using HTTPS
4. Enable debug logging:
   ```yaml
   logger:
     default: info
     logs:
       custom_components.seerr: debug
   ```

## Support

- Report issues on GitHub
- Check existing issues before creating new ones
- Include debug logs when reporting problems
