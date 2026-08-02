# Operator Guide — 57R337 $M4R7 NYC

## Day-to-Day Operations

### Starting the System

```bash
# Activate virtual environment
source venv/bin/activate

# Start the application
python run.py
```

The application will be available at `http://localhost:8080`.

### Using Docker Compose (Production)

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f web
```

### Monitoring

- **Dashboard**: http://localhost:8080 — Live campaign monitoring
- **Health Center**: http://localhost:8080/health — System health metrics
- **Logs**: Check `logs/` directory for application logs
- **Provider Status**: Provider Center shows real-time connection status

### Common Tasks

#### Launching a Campaign
1. Navigate to the Campaign Builder
2. Complete each step: Contacts → Audio → Templates → Caller Identity → Providers → Rules
3. Review on the Launch Review screen
4. Click "Launch Campaign"

#### Checking Provider Health
1. Go to Provider Center
2. Check status indicators (green = connected, yellow = expired, red = needs login, gray = disabled)
3. Click "Test All" to verify all connections
4. Use "Reconnect All Expired" for any expired providers

#### Managing Files
1. Go to Upload Center
2. Upload files using drag-and-drop or click-to-browse
3. Validate files (format, size, content)
4. Preview files before using in campaigns
5. Replace or archive old versions

#### Monitoring Live Campaigns
1. Go to Mission Control (Live Operations)
2. View real-time progress pipeline
3. Monitor provider health panel
4. Check live event feed
5. Use pause/stop controls as needed

### Troubleshooting

#### Campaign won't start
- Check that all providers are connected (green status)
- Verify contact list is uploaded and validated
- Check that all required assets are uploaded
- Review the Launch Review screen for warnings

#### Provider connection lost
- Check provider status in Provider Center
- Click "Reconnect" on the affected provider
- If using failover, the system will automatically switch to backup
- Check logs for error details

#### High latency or slow performance
- Check Health Center for CPU/memory/disk metrics
- Review queue depth in Queue Visualization
- Check provider latency in Provider Center
- Reduce concurrent calls/messages if needed

### Maintenance

#### Database Backups
- Configure backup settings in Settings
- Backups run automatically based on schedule
- Manual backup: `flask db export`

#### Log Rotation
- Logs rotate daily and by size
- Old logs are automatically archived
- Configure retention policy in Settings

#### Updates
- Pull latest code from repository
- Run migrations: `flask db upgrade`
- Restart the application
- Verify health check passes
