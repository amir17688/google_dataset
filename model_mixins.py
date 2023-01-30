class CommunicationPreferenceMixin(object):

    @classmethod
    def get_default_methods(cls):
        """
            We want to set every value in the bitfield to 1.
        """
        return 2 ** len(cls.COMMUNICATION_METHODS) - 1

    def get_descriptions(self):
        key = self.CommunicationType(self.communication_type)
        return self.COMMUNICATION_TYPE_DESCRIPTIONS[key]

    def can_slack(self):
        """
            Boolean of whether or not the Worker wants slack messages
            for the CommunicationType.
        """
        return self.methods.slack

    def can_email(self):
        """
            Boolean of whether or not the Worker wants email messages
            for the CommunicationType.
        """
        return self.methods.email

    def __str__(self):
        return '{} - {} - {}'.format(
            self.worker,
            self.methods.items(),
            self.get_comunication_type_description()
        )


class StaffingRequestMixin(object):

    def get_request_cause_description(self):
        return self.RequestCause(self.request_cause).description

    def __str__(self):
        return '{} - {} - {}'.format(
            self.worker,
            self.task.id,
            self.get_request_cause_description()
        )


class StaffingResponseMixin(object):

    def __str__(self):
        return '{} - {} - {}'.format(
            self.request,
            self.is_available,
            self.is_winner
        )
)):
                raise ModelSaveError('You are trying to add a reviewer '
                                     'certification ({}) for a worker without '
                                     'an entry-level certification'
                                     .format(self))
        super().save(*args, **kwargs)


class ProjectMixin(object):

    def __str__(self):
        return '{} ({})'.format(str(self.workflow_version.slug),
                                self.short_description)


class TaskMixin(object):

    def __str__(self):
        return '{} - {}'.format(str(self.project), str(self.step.slug))


class TaskAssignmentMixin(object):

    def save(self, *args, **kwargs):
        if self.task.step.is_human:
            if self.worker is None:
                raise ModelSaveError('Worker has to be present '
                                     'if worker type is Human')
        else:
            if self.worker is not None:
                raise ModelSaveError('Worker should not be assigned '
                                     'if worker type is Machine')

        super().save(*args, **kwargs)

    def __str__(self):
        return '{} - {} - {}'.format(
            str(self.task), self.assignment_counter, str(self.worker))


class PayRateMixin(object):

    def __str__(self):
        return '{} ({} - {})'.format(
            self.worker, self.start_date, self.end_date or 'now')

    def save(self, *args, **kwargs):
        if self.end_date and self.end_date < self.start_date:
            raise ModelSaveError('end_date must be greater than '
                                 'start_date')

        if self.end_date is None:
            # If end_date is None, need to check that no other PayRates have
            # end_date is None, nor do they overlap.
            if type(self).objects.exclude(id=self.id).filter(
                    (Q(end_date__gte=self.start_date) |
                     Q(end_date__isnull=True)),
                    worker=self.worker).exists():
                raise ModelSaveError(
                    'Date range overlaps with existing PayRate entry')
        else:
            # If end_date is not None, need to check if other PayRates overlap.
            if (type(self).objects.exclude(id=self.id).filter(
                    start_date__lte=self.end_date,
                    end_date__isnull=True,
                    worker=self.worker).exists() or
                type(self).objects.exclude(id=self.id).filter(
                    (Q(start_date__lte=self.end_date) &
                     Q(end_date__gte=self.start_date)),
                    worker=self.worker).exists()):
                raise ModelSaveError(
                    'Date range overlaps with existing PayRate entry')
        super().save(*args, **kwargs)
