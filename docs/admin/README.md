# Administrator Guide — 57R337 $M4R7 NYC

## System Administration

### Configuration

#### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Environment (development/staging/production) | development |
| `DATABASE_URL` | PostgreSQL connection string | sqlite:///app.db |
| `REDIS_URL` | Redis connection string | redis://localhost:6379/0 |
| `SECRET_KEY` | Flask secret key | (must be set) |
| `MAX_FILE_SIZE` | Maximum upload size in bytes | 52428800 |
| `ALLOWED_EXTENSIONS` | Comma-separated list of allowed file extensions | txt,csv,xlsx,wav,mp3,ogg,flac,m4a,html,pdf,png,jpg |

#### Settings Management
1. Navigate to Settings page
2. Configure application-wide settings (timezone, language, date format)
3. Set system limits (max file size, storage paths)
4. Configure UI preferences (theme)
5. Set notification preferences
6. Configure backup settings
7. Configure export settings

### User Management

#### Roles
| Role | Permissions |
|------|-------------|
| Admin | Full access to all features and settings |
| Manager | Create/launch campaigns, manage users, view analytics |
| Operator | Launch and monitor campaigns, manage contacts |
| Viewer | View campaigns and reports only |

#### Managing Users
1. Navigate to Settings → Users
2. Add new users with email, name, and role
3. Edit or remove existing users
4. Reset passwords as needed
5. View activity log for all user actions

### Provider Management

#### Connecting a Provider
1. Navigate to Provider Center
2. Select provider type (Voice or Messaging)
3. Choose provider from the list
4. Enter connection credentials
5. Click "Test" to verify connection
6. Set priority for failover ordering
7. Enable/disable as needed

#### Provider Health Monitoring
- Green: Connected and healthy
- Yellow: Expired (needs re-authentication)
- Red: Needs login (not connected)
- Gray: Disabled (turned off)

### Campaign Management

#### Creating a Campaign
1. Navigate to Campaigns → New Campaign
2. Select campaign type (Voice, SMS, Email, Mixed)
3. Configure campaign settings
4. Upload contact list
5. Upload audio files and templates
6. Configure caller identity
7. Select providers
8. Set campaign rules
9. Review on Launch Review screen
10. Launch campaign

#### Monitoring Campaigns
1. Navigate to Mission Control
2. View real-time progress pipeline
3. Monitor provider health
4. Check live event feed
5. Use pause/stop controls as needed

### System Health

#### Health Center
The Health Center provides real-time system metrics:
- CPU usage
- Memory usage
- Disk usage
- Network status
- Provider connectivity
- Queue depth
- Error rates

#### Alerts
The system generates alerts when:
- CPU usage exceeds 80%
- Memory usage exceeds 85%
- Disk usage exceeds 90%
- Provider connection is lost
- Queue depth exceeds threshold
- Error rate exceeds threshold

### Backup and Recovery

#### Backup Configuration
1. Navigate to Settings → Backup
2. Set backup frequency (daily, weekly, monthly)
3. Set retention period (number of backups to keep)
4. Set backup location (local or S3)
5. Enable automatic backups

#### Disaster Recovery
1. Restore from latest backup
2. Verify database integrity
3. Reconnect all providers
4. Verify file storage integrity
5. Test campaign execution

### Security

#### Best Practices
- Use strong secret keys (change default in production)
- Enable HTTPS (configure SSL in nginx)
- Enable MFA for admin users
- Regularly rotate API keys
- Review audit logs regularly
- Keep dependencies updated
- Restrict IP access if needed

#### Compliance
The system supports compliance with:
- **GDPR**: Consent tracking, data export, data deletion
- **TCPA**: Do-not-call list, consent tracking, audit logging
- **CAN-SPAM**: Unsubscribe links, sender identification

### API Management

#### API Keys
1. Navigate to Settings → API
2. Generate new API keys
3. Set rate limits per key
4. Revoke compromised keys
5. Rotate keys regularly

#### Webhooks
1. Navigate to Settings → Webhooks
2. Configure webhook URLs
3. Select event types to subscribe to
4. Test webhook delivery
5. Monitor delivery status
