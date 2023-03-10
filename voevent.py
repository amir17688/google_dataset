# Comet VOEvent Broker.
# VOEvent message parsing & definition.

# Python standard library
import re
from datetime import datetime

# XML parsing using lxml
import lxml.etree as ElementTree

from comet import __version__, __url__
import comet.log as log
from comet.utility.xml import xml_document

__all__ = ["parse_ivorn", "broker_test_message"]

ElementTree.register_namespace("voe", "http://www.ivoa.net/xml/VOEvent/v2.0")

IVORN_RE = re.compile("""ivo://
                         (?P<auth>[a-zA-Z0-9][\w\-.~*'()]{2,}) /     # Authority
                         (?P<rsrc>[\w\-\.~\*'()/]*) \#?              # Resource name
                         (?P<localID>[\w\-\.~\*'()\+=/%!$&,;:@?]*) $ # Fragment
                      """, re.VERBOSE)

def parse_ivorn(ivorn):
    """
    Takes an IVORN of the form

        ivo://authorityID/resourceKey#local_ID

    and returns (authorityID, resourceKey, local_ID). Raise if that isn't
    possible.

    Refer to the IVOA Identifiers Recommendation (1.12) for justification, but
    note that document is not as clear as unambiguous as one might hope. We
    have assumed that anything which is not explicitly permitted is forbitten
    in the authority and the resource name, while anything which would be
    permitted in an RFC-3986 URI is permitted in the fragment.
    """
    try:
        return IVORN_RE.match(ivorn).groups()
    except AttributeError as e:
        log.debug("Failed to parse as IVORN: ", str(e))
        raise Exception("Invalid IVORN: %s" % (ivorn,))

def broker_test_message(ivo):
    """
    Test message which is regularly broadcast to all subscribers.
    """
    root_element = ElementTree.Element("{http://www.ivoa.net/xml/VOEvent/v2.0}VOEvent",
        attrib={
            "ivorn": ivo + "#TestEvent-%s" % datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),
            "role": "test",
            "version": "2.0",
            "{http://www.w3.org/2001/XMLSchema-instance}schemaLocation": "http://www.ivoa.net/xml/VOEvent/v2.0 http://www.ivoa.net/xml/VOEvent/VOEvent-v2.0.xsd"
        }
    )
    who = ElementTree.SubElement(root_element, "Who")
    author_ivorn = ElementTree.SubElement(who, "AuthorIVORN")
    author_ivorn.text = ivo
    date = ElementTree.SubElement(who, "Date")
    date.text = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")
    what = ElementTree.SubElement(root_element, "What")
    description =  ElementTree.SubElement(what, "Description")
    description.text = "Broker test event generated by Comet %s." % (__version__,)
    ElementTree.SubElement(what, "Reference", uri=__url__)
    return xml_document(root_element)
