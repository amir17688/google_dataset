from contextlib import contextmanager

from casexml.apps.case.mock import CaseFactory, CaseStructure, CaseIndex
from casexml.apps.case.models import CommCareCase, INDEX_ID_PARENT, INDEX_RELATIONSHIP_CHILD
from casexml.apps.case.signals import case_post_save
from corehq.apps.data_interfaces.models import (AutomaticUpdateRule,
    AutomaticUpdateRuleCriteria, AutomaticUpdateAction)
from corehq.apps.data_interfaces.tasks import run_case_update_rules_for_domain
from datetime import datetime, date

from corehq.form_processor.backends.sql.dbaccessors import CaseAccessorSQL
from corehq.form_processor.interfaces.dbaccessors import CaseAccessors
from corehq.form_processor.tests.utils import run_with_all_backends, FormProcessorTestUtils, set_case_property_directly
from corehq.form_processor.utils.general import should_use_sql_backend
from django.test import TestCase
from mock import patch

from corehq.util.context_managers import drop_connected_signals


class AutomaticCaseUpdateTest(TestCase):
    def setUp(self):
        self.domain = 'auto-update-test'
        self.case_db = CaseAccessors(self.domain)
        self.factory = CaseFactory(self.domain)
        self.rule = AutomaticUpdateRule(
            domain=self.domain,
            name='test-rule',
            case_type='test-case-type',
            active=True,
            server_modified_boundary=30,
        )
        self.rule.save()
        self.rule.automaticupdaterulecriteria_set = [
            AutomaticUpdateRuleCriteria(
                property_name='last_visit_date',
                property_value='30',
                match_type=AutomaticUpdateRuleCriteria.MATCH_DAYS_SINCE,
            ),
        ]
        self.rule.automaticupdateaction_set = [
            AutomaticUpdateAction(
                action=AutomaticUpdateAction.ACTION_UPDATE,
                property_name='update_flag',
                property_value='Y',
            ),
            AutomaticUpdateAction(
                action=AutomaticUpdateAction.ACTION_CLOSE,
            ),
        ]

        self.rule2 = AutomaticUpdateRule(
            domain=self.domain,
            name='test-rule-2',
            case_type='test-case-type-2',
            active=True,
            server_modified_boundary=30,
        )
        self.rule2.save()
        self.rule2.automaticupdateaction_set = [
            AutomaticUpdateAction(
                action=AutomaticUpdateAction.ACTION_CLOSE,
            ),
        ]

        self.rule3 = AutomaticUpdateRule(
            domain=self.domain,
            name='test-rule-3',
            case_type='test-case-type-2',
            active=True,
            server_modified_boundary=50,
        )
        self.rule3.save()
        self.rule3.automaticupdateaction_set = [
            AutomaticUpdateAction(
                action=AutomaticUpdateAction.ACTION_CLOSE,
            ),
        ]

        with drop_connected_signals(case_post_save):
            case = self.factory.create_case(case_type='test-case-type')
        self.case_id = case.case_id

    def tearDown(self):
        AutomaticUpdateRuleCriteria.objects.all().delete()
        AutomaticUpdateAction.objects.all().delete()
        AutomaticUpdateRule.objects.all().delete()
        FormProcessorTestUtils.delete_all_cases(self.domain)

    def _get_case_ids(self, *args, **kwargs):
        return [self.case_id]

    def _get_case(self):
        return self.case_db.get_case(self.case_id)

    def _assert_case_revision(self, rev_number, last_modified, expect_modified=False):
        if should_use_sql_backend(self.domain):
            self.assertEqual(
                expect_modified,
                CaseAccessorSQL.case_modified_since(self.case_id, last_modified)
            )
        else:
            doc = self._get_case()
            self.assertTrue(doc['_rev'].startswith('%s-' % rev_number))

    @run_with_all_backends
    def test_rule(self):
        now = datetime(2015, 10, 22, 0, 0)
        with patch('corehq.apps.data_interfaces.models.AutomaticUpdateRule.get_case_ids', new=self._get_case_ids):
            # No update: both dates are 27 days away
            last_modified = datetime(2015, 9, 25, 12, 0)
            _update_case(self.domain, self.case_id, last_modified, date(2015, 9, 25))
            self._assert_case_revision(2, last_modified)
            run_case_update_rules_for_domain(self.domain, now=now)
            self._assert_case_revision(2, last_modified)

            # No update: server_modified_on is 32 days away but last_visit_date is 27 days away
            last_modified = datetime(2015, 9, 20, 12, 0)
            _update_case(self.domain, self.case_id, last_modified, date(2015, 9, 25))
            self._assert_case_revision(3, last_modified)
            run_case_update_rules_for_domain(self.domain, now=now)
            self._assert_case_revision(3, last_modified)

            # No update: last_visit_date is 32 days away but server_modified_on is 27 days away
            last_modified = datetime(2015, 9, 25, 12, 0)
            _update_case(self.domain, self.case_id, last_modified, date(2015, 9, 20))
            self._assert_case_revision(4, last_modified)
            run_case_update_rules_for_domain(self.domain, now=now)
            self._assert_case_revision(4, last_modified)

            # Perform update: both dates are 32 days away
            last_modified = datetime(2015, 9, 20, 12, 0)
            _update_case(self.domain, self.case_id, last_modified, date(2015, 9, 20))
            self._assert_case_revision(5, last_modified)
            with drop_connected_signals(case_post_save):
                run_case_update_rules_for_domain(self.domain, now=now)
            self._assert_case_revision(6, last_modified, True)

            case = self._get_case()
            self.assertEqual(case.get_case_property('update_flag'), 'Y')
            self.assertEqual(case.closed, True)

    @run_with_all_backends
    def test_match_days_since(self):
        with _with_case(self.domain, 'test-case-type-2', datetime(2015, 1, 1)) as case:
            self.rule2.automaticupdaterulecriteria_set = [
                AutomaticUpdateRuleCriteria(
                    property_name='last_visit_date',
                    property_value='30',
                    match_type=AutomaticUpdateRuleCriteria.MATCH_DAYS_SINCE,
                ),
            ]
            self.assertFalse(self.rule2.rule_matches_case(case, datetime(2016, 1, 1)))

            set_case_property_directly(case, 'last_visit_date', '2015-12-30')
            self.assertFalse(self.rule2.rule_matches_case(case, datetime(2016, 1, 1)))

            set_case_property_directly(case, 'last_visit_date', '2015-12-03')
            self.assertFalse(self.rule2.rule_matches_case(case, datetime(2016, 1, 1)))

            set_case_property_directly(case, 'last_visit_date', '2015-12-02')
            self.assertTrue(self.rule2.rule_matches_case(case, datetime(2016, 1, 1)))

            set_case_property_directly(case, 'last_visit_date', '2015-11-01')
            self.assertTrue(self.rule2.rule_matches_case(case, datetime(2016, 1, 1)))

    @run_with_all_backends
    def test_match_equal(self):
        with _with_case(self.domain, 'test-case-type-2', datetime(2015, 1, 1)) as case:
            self.rule2.automaticupdaterulecriteria_set = [
                AutomaticUpdateRuleCriteria(
                    property_name='property1',
                    property_value='value1',
                    match_type=AutomaticUpdateRuleCriteria.MATCH_EQUAL,
                ),
            ]
            self.assertFalse(self.rule2.rule_matches_case(case, datetime(2016, 1, 1)))

            set_case_property_directly(case, 'property1', 'x')
            self.assertFalse(self.rule2.rule_matches_case(case, datetime(2016, 1, 1)))

            set_case_property_directly(case, 'property1', 'value1')
            self.assertTrue(self.rule2.rule_matches_case(case, datetime(2016, 1, 1)))

    @run_with_all_backends
    def test_match_not_equal(self):
        with _with_case(self.domain, 'test-case-type-2', datetime(2015, 1, 1)) as case:
            self.rule2.automaticupdaterulecriteria_set = [
                AutomaticUpdateRuleCriteria(
                    property_name='property2',
                    property_value='value2',
                    match_type=AutomaticUpdateRuleCriteria.MATCH_NOT_EQUAL,
                ),
            ]
            self.assertTrue(self.rule2.rule_matches_case(case, datetime(2016, 1, 1)))

            set_case_property_directly(case, 'property2', 'value2')
            self.assertFalse(self.rule2.rule_matches_case(case, datetime(2016, 1, 1)))

            set_case_property_directly(case, 'property2', 'x')
            self.assertTrue(self.rule2.rule_matches_case(case, datetime(2016, 1, 1)))

    @run_with_all_backends
    def test_date_case_properties_for_equality(self):
        """
        Date case properties are automatically converted from string to date
        when fetching from the db, so here we want to make sure this doesn't
        interfere with our ability to compare dates for equality.
        """
        with _with_case(self.domain, 'test-case-type-2', datetime(2015, 1, 1)) as case:
            self.rule2.automaticupdaterulecriteria_set = [
                AutomaticUpdateRuleCriteria(
                    property_name='property1',
                    property_value='2016-02-24',
                    match_type=AutomaticUpdateRuleCriteria.MATCH_EQUAL,
                ),
            ]

            set_case_property_directly(case, 'property1', '2016-02-24')
            self.assertTrue(self.rule2.rule_matches_case(case, datetime(2016, 1, 1)))

            set_case_property_directly(case, 'property1', '2016-02-25')
            self.assertFalse(self.rule2.rule_matches_case(case, datetime(2016, 1, 1)))

    @run_with_all_backends
    def test_date_case_properties_for_inequality(self):
        with _with_case(self.domain, 'test-case-type-2', datetime(2015, 1, 1)) as case:
            self.rule2.automaticupdaterulecriteria_set = [
                AutomaticUpdateRuleCriteria(
                    property_name='property1',
                    property_value='2016-02-24',
                    match_type=AutomaticUpdateRuleCriteria.MATCH_NOT_EQUAL,
                ),
            ]

            set_case_property_directly(case, 'property1', '2016-02-24')
            self.assertFalse(self.rule2.rule_matches_case(case, datetime(2016, 1, 1)))

            set_case_property_directly(case, 'property1', '2016-02-25')
            self.assertTrue(self.rule2.rule_matches_case(case, datetime(2016, 1, 1)))

    @run_with_all_backends
    def test_match_has_value(self):
        with _with_case(self.domain, 'test-case-type-2', datetime(2015, 1, 1)) as case:
            self.rule2.automaticupdaterulecriteria_set = [
                AutomaticUpdateRuleCriteria(
                    property_name='property3',
                    match_type=AutomaticUpdateRuleCriteria.MATCH_HAS_VALUE,
                ),
            ]
            self.assertFalse(self.rule2.rule_matches_case(case, datetime(2016, 1, 1)))

            set_case_property_directly(case, 'property3', 'x')
            self.assertTrue(self.rule2.rule_matches_case(case, datetime(2016, 1, 1)))

            set_case_property_directly(case, 'property3', '')
            self.assertFalse(self.rule2.rule_matches_case(case, datetime(2016, 1, 1)))

    @run_with_all_backends
    def test_and_criteria(self):
        with _with_case(self.domain, 'test-case-type-2', datetime(2015, 1, 1)) as case:

            self.rule2.automaticupdaterulecriteria_set = [
                AutomaticUpdateRuleCriteria(
                    property_name='last_visit_date',
                    property_value='30',
                    match_type=AutomaticUpdateRuleCriteria.MATCH_DAYS_SINCE,
                ),
                AutomaticUpdateRuleCriteria(
                    property_name='property1',
                    property_value='value1',
                    match_type=AutomaticUpdateRuleCriteria.MATCH_EQUAL,
                ),
                AutomaticUpdateRuleCriteria(
                    property_name='property2',
                    property_value='value2',
                    match_type=AutomaticUpdateRuleCriteria.MATCH_NOT_EQUAL,
                ),
                AutomaticUpdateRuleCriteria(
                    property_name='property3',
                    match_type=AutomaticUpdateRuleCriteria.MATCH_HAS_VALUE,
                ),
            ]

            set_case_property_directly(case, 'last_visit_date', '2015-11-01')
            set_case_property_directly(case, 'property1', 'value1')
            set_case_property_directly(case, 'property2', 'x')
            set_case_property_directly(case, 'property3', 'x')
            self.assertTrue(self.rule2.rule_matches_case(case, datetime(2016, 1, 1)))

            set_case_property_directly(case, 'last_visit_date', '2015-12-30')
            self.assertFalse(self.rule2.rule_matches_case(case, datetime(2016, 1, 1)))

            set_case_property_directly(case, 'last_visit_date', '2015-11-01')
            set_case_property_directly(case, 'property1', 'x')
            self.assertFalse(self.rule2.rule_matches_case(case, datetime(2016, 1, 1)))

            set_case_property_directly(case, 'property1', 'value1')
            set_case_property_directly(case, 'property2', 'value2')
            self.assertFalse(self.rule2.rule_matches_case(case, datetime(2016, 1, 1)))

            set_case_property_directly(case, 'property2', 'x')
            set_case_property_directly(case, 'property3', '')
            self.assertFalse(self.rule2.rule_matches_case(case, datetime(2016, 1, 1)))

            set_case_property_directly(case, 'property3', 'x')
            self.assertTrue(self.rule2.rule_matches_case(case, datetime(2016, 1, 1)))

    def test_get_rules_from_domain(self):
        rules = AutomaticUpdateRule.by_domain(self.domain)
        rules_by_case_type = AutomaticUpdateRule.organize_rules_by_case_type(rules)

        expected_case_types = ['test-case-type', 'test-case-type-2']
        actual_case_types = rules_by_case_type.keys()
        self.assertEqual(set(expected_case_types), set(actual_case_types))

        expected_rule_ids = [self.rule.pk]
        actual_rule_ids = [rule.pk for rule in rules_by_case_type['test-case-type']]
        self.assertEqual(set(expected_rule_ids), set(actual_rule_ids))

        expected_rule_ids = [self.rule2.pk, self.rule3.pk]
        actual_rule_ids = [rule.pk for rule in rules_by_case_type['test-case-type-2']]
        self.assertEqual(set(expected_rule_ids), set(actual_rule_ids))

    def test_boundary_date(self):
        rules = AutomaticUpdateRule.by_domain(self.domain)
        rules_by_case_type = AutomaticUpdateRule.organize_rules_by_case_type(rules)

        boundary_date = AutomaticUpdateRule.get_boundary_date(
            rules_by_case_type['test-case-type'], datetime(2016, 1, 1))
        self.assertEqual(boundary_date, datetime(2015, 12, 2))

        boundary_date = AutomaticUpdateRule.get_boundary_date(
            rules_by_case_type['test-case-type-2'], datetime(2016, 1, 1))
        self.assertEqual(boundary_date, datetime(2015, 12, 2))

    @run_with_all_backends
    def test_parent_case_lookup(self):
        with _with_case(self.domain, 'test-child-case-type', datetime(2016, 1, 1)) as child, \
                _with_case(self.domain, 'test-parent-case-type', datetime(2016, 1, 1), case_name='abc') as parent:

            # Set the parent case relationship
            child = set_parent_case(self.domain, child, parent)

            # Create a rule that references parent/name which should match
            rule = AutomaticUpdateRule(
                domain=self.domain,
                name='test-parent-rule',
                case_type='test-child-case-type',
                active=True,
                server_modified_boundary=30,
            )
            rule.save()
            self.addCleanup(rule.delete)
            rule.automaticupdaterulecriteria_set = [
                AutomaticUpdateRuleCriteria(
                    property_name='parent/name',
                    property_value='abc',
                    match_type=AutomaticUpdateRuleCriteria.MATCH_EQUAL,
                ),
            ]

            self.assertTrue(rule.rule_matches_case(child, datetime(2016, 3, 1)))

            # Update the rule to match on a different name and now it shouldn't match
            rule.automaticupdaterulecriteria_set.all().delete()
            rule.automaticupdaterulecriteria_set = [
                AutomaticUpdateRuleCriteria(
                    property_name='parent/name',
                    property_value='def',
                    match_type=AutomaticUpdateRuleCriteria.MATCH_EQUAL,
                ),
            ]

            self.assertFalse(rule.rule_matches_case(child, datetime(2016, 3, 1)))


@contextmanager
def _with_case(domain, case_type, last_modified, **kwargs):
    with drop_connected_signals(case_post_save):
        case = CaseFactory(domain).create_case(case_type=case_type, **kwargs)

    _update_case(domain, case.case_id, last_modified)
    accessors = CaseAccessors(domain)
    case = accessors.get_case(case.case_id)
    try:
        yield case
    finally:
        if should_use_sql_backend(domain):
            CaseAccessorSQL.hard_delete_cases(domain, [case.case_id])
        else:
            case.delete()


def _save_case(domain, case):
    if should_use_sql_backend(domain):
        CaseAccessorSQL.save_case(case)
    else:
        # can't call case.save() since it overrides the server_modified_on property
        CommCareCase.get_db().save_doc(case.to_json())


def _update_case(domain, case_id, server_modified_on, last_visit_date=None):
    accessors = CaseAccessors(domain)
    case = accessors.get_case(case_id)
    case.server_modified_on = server_modified_on
    if last_visit_date:
        set_case_property_directly(case, 'last_visit_date', last_visit_date.strftime('%Y-%m-%d'))
    _save_case(domain, case)


def set_parent_case(domain, child_case, parent_case):
    server_modified_on = child_case.server_modified_on

    parent = CaseStructure(case_id=parent_case.case_id)
    CaseFactory(domain).create_or_update_case(
        CaseStructure(
            case_id=child_case.case_id,
            indices=[CaseIndex(
                related_structure=parent,
                identifier=INDEX_ID_PARENT,
                relationship=INDEX_RELATIONSHIP_CHILD
            )],
        )
    )

    child_case = CaseAccessors(domain).get_case(child_case.case_id)
    child_case.server_modified_on = server_modified_on
    _save_case(domain, child_case)
    return CaseAccessors(domain).get_case(child_case.case_id)
