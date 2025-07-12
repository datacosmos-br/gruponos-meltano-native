# 🏗️ Operations Manual

## Daily Operations

### Morning Health Check

```bash
# 1. Check system status
make status

# 2. Review overnight logs
make logs

# 3. Validate Oracle data
make validate-oracle

# 4. Check for any errors
make analyze-failures
```

### Starting Data Sync

```bash
# For regular incremental updates
make incremental-sync

# For full data refresh (weekly)
make full-sync
```

### Monitoring During Operations

```bash
# Real-time monitoring
make monitor

# Check specific processes
ps aux | grep meltano
```

## Production Deployment Checklist

### Pre-Deployment

- [ ] All tests pass in staging environment
- [ ] Database connections verified
- [ ] SSL certificates valid
- [ ] Monitoring systems operational
- [ ] Backup procedures verified

### Deployment Steps

1. **Stop current processes**

   ```bash
   make stop-sync
   ```

2. **Deploy new code**

   ```bash
   git pull origin main
   ```

3. **Update dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Test environment**

   ```bash
   make env
   make validate-oracle
   ```

5. **Start services**

   ```bash
   make incremental-sync
   ```

6. **Verify operation**

   ```bash
   make status
   make monitor
   ```

### Post-Deployment

- Monitor for 1 hour after deployment
- Check error rates in logs
- Validate data quality
- Update operational dashboard

## Incident Response

### Severity Levels

#### Critical (P0)

- Data sync completely stopped
- Oracle database connection lost
- Data corruption detected

**Response**: Immediate investigation, escalate to on-call engineer

#### High (P1)

- Sync failures with retries
- Performance degradation >50%
- SSL certificate issues

**Response**: Investigate within 2 hours

#### Medium (P2)

- Intermittent validation errors
- Minor performance issues
- Non-critical warnings

**Response**: Investigate within 24 hours

### Escalation Procedures

1. **Check troubleshooting guide** (this document)
2. **Review recent logs** for error patterns
3. **Test basic connectivity** to Oracle systems
4. **If unresolved**, escalate to:
   - Database team (Oracle issues)
   - Network team (connectivity)
   - Development team (application logic)

## Performance Monitoring

### Key Metrics

- **Sync Duration**: Should complete within expected timeframes
- **Record Count**: Monitor for unexpected drops
- **Error Rate**: Should be <1% under normal conditions
- **Connection Time**: Oracle connections should establish <10 seconds

### Performance Optimization

#### For Slow Syncs

```bash
# Reduce batch size temporarily
# Edit meltano.yml:
# page_size: 10  # Smaller batches
# batch_size_rows: 50
```

#### For High Error Rates

```bash
# Increase retry attempts
export FLEXT_TARGET_ORACLE_RETRIES=5
export FLEXT_TARGET_ORACLE_RETRY_DELAY=10
```

## Backup and Recovery

### State Backup

```bash
# Backup current Meltano state
cp -r .meltano/run/state backup/state_$(date +%Y%m%d_%H%M%S)

# Backup configuration
cp meltano.yml backup/meltano_$(date +%Y%m%d_%H%M%S).yml
```

### Recovery Procedures

```bash
# Restore from backup
cp backup/state_YYYYMMDD_HHMMSS/* .meltano/run/state/

# Reset to clean state if corrupted
make reset-state
```

## Maintenance Windows

### Weekly Maintenance

- **Every Sunday 2:00 AM**: Full sync execution
- **Every Sunday 3:00 AM**: Log cleanup
- **Every Sunday 4:00 AM**: Database statistics update

### Monthly Maintenance

- Review and archive old logs
- Update documentation
- Performance review and optimization
- SSL certificate renewal check

## Security Procedures

### Access Control

- Only authorized personnel have access to production environment
- All database passwords stored in secure environment variables
- SSL connections required for production

### Audit Trail

- All operations logged with timestamps
- Database access logged
- Configuration changes tracked in git

## Contact Information

### On-Call Schedule

- **Primary**: Development Team
- **Secondary**: Database Team
- **Escalation**: Infrastructure Team

### Emergency Contacts

- **Database Issues**: DBA Team
- **Network Issues**: Infrastructure Team
- **Security Issues**: Security Team
