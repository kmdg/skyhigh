'''
Created on 03 Jan 2013

@author: euan
'''
import pytz

DEFAULT_IMAGE_CATEGORY_PROFILE = 'profile'
DEFAULT_IMAGE_CATEGORY_PRESS_RELEASE = 'press release'
DEFAULT_IMAGE_CATEGORY_MEDIA_COVERAGE = 'media coverage'
DEFAULT_IMAGE_CATEGORY_EVENT = 'event'
DEFAULT_IMAGE_CATEGORY_RESOURCE = 'resource'

DEFAULT_IMAGE_CATEGORY_CHOICES = ((DEFAULT_IMAGE_CATEGORY_PROFILE, 'Profile'),
                                  (DEFAULT_IMAGE_CATEGORY_PRESS_RELEASE, 'Press Release'),
                                  (DEFAULT_IMAGE_CATEGORY_MEDIA_COVERAGE, 'Media Coverage'),
                                  (DEFAULT_IMAGE_CATEGORY_EVENT, 'Event'),
                                  (DEFAULT_IMAGE_CATEGORY_RESOURCE, 'Resource'),
                                  )

RESOURCE_TYPES = (('whitepapers', 'Whitepapers'),
                  ('datasheets', 'Datasheets'),
                  ('videos', 'Videos'),
                  ('ondemandwebinars', 'On-Demand Webinars'),
                  )

ROLE_CHOICE_END_USER = 0
ROLE_CHOICE_PRODUCT_OWNER = 100
ROLE_CHOICE_TECHNICAL_PARTNER = 200
ROLE_CHOICE_CLOUD_SERVICE_PROVIDER = 250
ROLE_CHOICE_DISTRIBUTOR = 300
ROLE_CHOICE_RESELLER = 350
ROLE_CHOICE_ADMIN = 400

ROLE_CHOICES = ((ROLE_CHOICE_END_USER, 'End User'),
                (ROLE_CHOICE_PRODUCT_OWNER, 'Product Evaluation Requester'),
                (ROLE_CHOICE_TECHNICAL_PARTNER, 'Technical Partner'),
                (ROLE_CHOICE_CLOUD_SERVICE_PROVIDER, 'Cloud Service Provider'),
                (ROLE_CHOICE_DISTRIBUTOR, 'Distributor'),
                (ROLE_CHOICE_RESELLER, 'Reseller'),
                (ROLE_CHOICE_ADMIN, 'Admin')
                )

TITLE_CHOICE_MR = 'Mr'
TITLE_CHOICE_MRS = 'Mrs'
TITLE_CHOICE_MISS = 'Miss'
TITLE_CHOICE_DR = 'Dr'
TITLE_CHOICE_PROF = 'Prof'

TITLE_CHOICES = ((TITLE_CHOICE_MR, 'Mr'),
                 (TITLE_CHOICE_MRS, 'Mrs'),
                 (TITLE_CHOICE_MISS, 'Miss'),
                 (TITLE_CHOICE_DR, 'Dr'),
                 (TITLE_CHOICE_PROF, 'Prof'),
                 )

TIMEZONE_CHOICES = ((tz, tz) for tz in pytz.common_timezones)

ACTIVITY_LOGIN = 'logged in'
ACTIVITY_LOGOUT = 'logged out'
ACTIVITY_ACTION_CREATE = 'created'
ACTIVITY_ACTION_UPDATE = 'updated'
ACTIVITY_ACTION_COMMENT = 'commented'
ACTIVITY_ACTION_BLOG_ENTRY_COMMENT = 'commented on blog entry'
ACTIVITY_ACTION_EVALUATION_REQUEST = 'product evaluation request'
ACTIVITY_ACTION_EVALUATION_REQUEST_APPROVED = 'product evaluation request approved'
ACTIVITY_ACTION_PARTNERSHIP_REQUEST = 'partnership request'
ACTIVITY_ACTION_PARTNERSHIP_REQUEST_APPROVED = 'partnership request approved'
ACTIVITY_ACTION_CONTACT_MESSAGE_SENT = 'contact message sent'
ACTIVITY_ACTION_CONTACT_MESSAGE_READ = 'contact message read'
ACTIVITY_ACTION_CONTACT_MESSAGE_RESPONDED = 'contact message responded'
ACTIVITY_ACTION_SUPPORT_CASE_SUBMITTED = 'support case submitted'

ACTIVITY_MODERATE_APPROVE = 'approved comment'
ACTIVITY_MODERATE_UNAPPROVE = 'unapproved comment'
ACTIVITY_MODERATE_SPAM = 'marked as spam'
ACTIVITY_MODERATE_BLACKLIST = 'blacklisted'
ACTIVITY_MODERATE_UNBLACKLIST = 'unblacklisted'

ACTION_CHOICES = ((ACTIVITY_LOGIN, 'logged in'),
                  (ACTIVITY_LOGOUT, 'logged out'),
                  (ACTIVITY_ACTION_CREATE, 'created'),
                  (ACTIVITY_ACTION_UPDATE, 'updated'),
                  (ACTIVITY_ACTION_COMMENT, 'commented on'),
                  (ACTIVITY_ACTION_BLOG_ENTRY_COMMENT, 'commented on blog entry'),
                  (ACTIVITY_MODERATE_APPROVE, 'updated the status to "Approved"'),
                  (ACTIVITY_MODERATE_UNAPPROVE, 'updated the status to "Unapproved"'),
                  (ACTIVITY_MODERATE_SPAM, 'updated the status to "Spam"'),
                  (ACTIVITY_MODERATE_BLACKLIST, 'blacklisted'),
                  (ACTIVITY_MODERATE_UNBLACKLIST, 'unblacklisted'),
                  (ACTIVITY_ACTION_CONTACT_MESSAGE_SENT, 'sent contact message'),
                  (ACTIVITY_ACTION_CONTACT_MESSAGE_READ, 'read contact message'),
                  (ACTIVITY_ACTION_CONTACT_MESSAGE_RESPONDED, 'responded to contact message'),
                  (ACTIVITY_ACTION_SUPPORT_CASE_SUBMITTED, 'submitted support case')
                  )

ACTION_POINTS = {ACTIVITY_LOGIN: 5,
                 ACTIVITY_LOGOUT: 5,
                 ACTIVITY_ACTION_BLOG_ENTRY_COMMENT: 5,
                 ACTIVITY_ACTION_EVALUATION_REQUEST: 5,
                 ACTIVITY_ACTION_EVALUATION_REQUEST_APPROVED: 10,
                 ACTIVITY_ACTION_PARTNERSHIP_REQUEST: 5,
                 ACTIVITY_ACTION_PARTNERSHIP_REQUEST_APPROVED: 10,
                 ACTIVITY_ACTION_CONTACT_MESSAGE_SENT: 5,
                 ACTIVITY_ACTION_SUPPORT_CASE_SUBMITTED: 5
                 }

PARTNERSHIP_REQUEST_STATUS_PENDING = 0
PARTNERSHIP_REQUEST_STATUS_APPROVED = 1
PARTNERSHIP_REQUEST_STATUS_DECLINED = 2

PARTNERSHIP_REQUEST_STATUS_CHOICES = ((PARTNERSHIP_REQUEST_STATUS_PENDING, 'Pending'),
                                      (PARTNERSHIP_REQUEST_STATUS_APPROVED, 'Approved'),
                                      (PARTNERSHIP_REQUEST_STATUS_DECLINED, "Declined")
                                      )

PRODUCT_EVALUATION_STATUS_PENDING = 0
PRODUCT_EVALUATION_STATUS_APPROVED = 1
PRODUCT_EVALUATION_STATUS_DECLINED = 2

PRODUCT_EVALUATION_STATUS_CHOICES = ((PRODUCT_EVALUATION_STATUS_PENDING,'Pending'),
                                     (PRODUCT_EVALUATION_STATUS_APPROVED,'Approved'),
                                     (PRODUCT_EVALUATION_STATUS_DECLINED,'Declined'),
                                     )

PARTNER_TYPE_TECHNOLOGY = 0
PARTNER_TYPE_CHANNEL = 1

PARTNER_TYPE_CHOICES = ((PARTNER_TYPE_TECHNOLOGY, 'Technology'),
                        (PARTNER_TYPE_CHANNEL, 'Channel'))

CHANNEL_PARTNER_TYPE_RESELLER = 0
CHANNEL_PARTNER_TYPE_DISTRIBUTOR = 1

CHANNEL_PARTNER_TYPE_CHOICES = ((CHANNEL_PARTNER_TYPE_RESELLER, 'Reseller'),
                        (PARTNER_TYPE_CHANNEL, 'Distributor'))

CONTACT_MESSAGE_STATUS_UNREAD = 0
CONTACT_MESSAGE_STATUS_READ = 1
CONTACT_MESSAGE_STATUS_RESPONDED = 2

CONTACT_MESSAGE_STATUS_CHOICES = ((CONTACT_MESSAGE_STATUS_UNREAD,'Unread'),
                                  (CONTACT_MESSAGE_STATUS_READ,'Read'),
                                  (CONTACT_MESSAGE_STATUS_RESPONDED,'Responded'),
                                  )

CSP_ATTRIBUTE_CATEGORY_DATA = 0
CSP_ATTRIBUTE_CATEGORY_USER_OR_DEVICE = 1
CSP_ATTRIBUTE_CATEGORY_SERVICE = 2
CSP_ATTRIBUTE_CATEGORY_BUSINESS_RISK = 3
CSP_ATTRIBUTE_CATEGORY_LEGAL = 4

CSP_ATTRIBUTE_CATEGORY_CHOICES = ((CSP_ATTRIBUTE_CATEGORY_DATA, 'Data'),
                                  (CSP_ATTRIBUTE_CATEGORY_USER_OR_DEVICE, 'User / Device'),
                                  (CSP_ATTRIBUTE_CATEGORY_SERVICE, 'Service'),
                                  (CSP_ATTRIBUTE_CATEGORY_BUSINESS_RISK, 'Business Risk'),
                                  (CSP_ATTRIBUTE_CATEGORY_LEGAL, 'Legal'))

CSP_CATEGORY_CLOUD_STORAGE = 0
CSP_CATEGORY_CRM = 1
CSP_CATEGORY_CLOUD_INFRASTRUCTURE = 2
CSP_CATEGORY_COLLABORATION = 3
CSP_CATEGORY_MARKETING = 4
CSP_CATEGORY_ERP = 5
CSP_CATEGORY_FINANCIAL_AND_ACCOUNTING = 6
CSP_CATEGORY_BILLING = 7
CSP_CATEGORY_OTHER = 8

CSP_CATEGORY_CHOICES = ((CSP_CATEGORY_BILLING, 'Billing'),
                        (CSP_CATEGORY_CLOUD_STORAGE, 'Cloud Storage'),
                        (CSP_CATEGORY_CRM, 'CRM'),
                        (CSP_CATEGORY_CLOUD_INFRASTRUCTURE, 'Cloud Infrastructure'),
                        (CSP_CATEGORY_COLLABORATION, 'Collaboration'),
                        (CSP_CATEGORY_ERP, 'ERP'),
                        (CSP_CATEGORY_FINANCIAL_AND_ACCOUNTING, 'Financial & Accounting'),
                        (CSP_CATEGORY_MARKETING, 'Marketing'),
                        (CSP_CATEGORY_OTHER, 'Other'),)


INDUSTRY_CHOICE_AGRICULTURE = 0
INDUSTRY_CHOICE_APPAREL = 1
INDUSTRY_CHOICE_BANKING = 2
INDUSTRY_CHOICE_BIOTECHNOLOGY = 3
INDUSTRY_CHOICE_CHEMICALS = 4
INDUSTRY_CHOICE_COMMUNICATIONS = 5
INDUSTRY_CHOICE_CONSTRUCTION = 6
INDUSTRY_CHOICE_CONSULTING = 7
INDUSTRY_CHOICE_EDUCATION = 8
INDUSTRY_CHOICE_ELECTRONICS = 9
INDUSTRY_CHOICE_ENERGY = 10
INDUSTRY_CHOICE_ENGINEERING = 11
INDUSTRY_CHOICE_ENTERTAINMENT = 12
INDUSTRY_CHOICE_ENVIRONMENTAL = 13
INDUSTRY_CHOICE_FINANCE = 14
INDUSTRY_CHOICE_FOOD_AND_BEVERAGE = 15
INDUSTRY_CHOICE_GOVERNMENT = 16
INDUSTRY_CHOICE_HEALTHCARE = 17
INDUSTRY_CHOICE_HOSPITALITY = 18
INDUSTRY_CHOICE_INSURANCE = 19
INDUSTRY_CHOICE_MACHINERY = 20
INDUSTRY_CHOICE_MANUFACTURING = 21
INDUSTRY_CHOICE_MEDIA = 22
INDUSTRY_CHOICE_NON_PROFIT = 23
INDUSTRY_CHOICE_OTHER = 24
INDUSTRY_CHOICE_RECREATION = 25
INDUSTRY_CHOICE_RETAIL = 26
INDUSTRY_CHOICE_SHIPPING = 27
INDUSTRY_CHOICE_TECHNOLOGY = 28
INDUSTRY_CHOICE_TELECOMMUNICATIONS = 29
INDUSTRY_CHOICE_TRANSPORTATION = 30
INDUSTRY_CHOICE_UTILITIES = 31

INDUSTRY_CHOICES = ((INDUSTRY_CHOICE_AGRICULTURE, 'Agriculture'),
                    (INDUSTRY_CHOICE_APPAREL, 'Apparel'),
                    (INDUSTRY_CHOICE_BANKING, 'Banking'),
                    (INDUSTRY_CHOICE_BIOTECHNOLOGY, 'Biotechnology'),
                    (INDUSTRY_CHOICE_CHEMICALS, 'Chemicals'),
                    (INDUSTRY_CHOICE_COMMUNICATIONS, 'Communications'),
                    (INDUSTRY_CHOICE_CONSTRUCTION, 'Construction'),
                    (INDUSTRY_CHOICE_CONSULTING, 'Consulting'),
                    (INDUSTRY_CHOICE_EDUCATION, 'Education'),
                    (INDUSTRY_CHOICE_ELECTRONICS, 'Electronics'),
                    (INDUSTRY_CHOICE_ENERGY, 'Energy'),
                    (INDUSTRY_CHOICE_ENGINEERING, 'Engineering'),
                    (INDUSTRY_CHOICE_ENTERTAINMENT, 'Entertainment'),
                    (INDUSTRY_CHOICE_ENVIRONMENTAL, 'Environmental'),
                    (INDUSTRY_CHOICE_FINANCE, 'Finance'),
                    (INDUSTRY_CHOICE_FOOD_AND_BEVERAGE, 'Food & Beverage'),
                    (INDUSTRY_CHOICE_GOVERNMENT, 'Government'),
                    (INDUSTRY_CHOICE_HEALTHCARE, 'Healthcare'),
                    (INDUSTRY_CHOICE_HOSPITALITY, 'Hospitality'),
                    (INDUSTRY_CHOICE_INSURANCE, 'Insurance'),
                    (INDUSTRY_CHOICE_MACHINERY, 'Machinery'),
                    (INDUSTRY_CHOICE_MANUFACTURING, 'Manufacturing'),
                    (INDUSTRY_CHOICE_MEDIA, 'Media'),
                    (INDUSTRY_CHOICE_NON_PROFIT, 'Not for profit'),
                    (INDUSTRY_CHOICE_OTHER, 'Other'),
                    (INDUSTRY_CHOICE_RECREATION, 'Recreation'),
                    (INDUSTRY_CHOICE_RETAIL, 'Retail'),
                    (INDUSTRY_CHOICE_SHIPPING, 'Shipping'),
                    (INDUSTRY_CHOICE_TECHNOLOGY, 'Technology'),
                    (INDUSTRY_CHOICE_TELECOMMUNICATIONS, 'Telecommunications'),
                    (INDUSTRY_CHOICE_TRANSPORTATION, 'Transportation'),
                    (INDUSTRY_CHOICE_UTILITIES, 'Utilities'),)

NUM_EMPLOYEES_CHOICE_1 = 0
NUM_EMPLOYEES_CHOICE_2 = 1
NUM_EMPLOYEES_CHOICE_3 = 2
NUM_EMPLOYEES_CHOICE_4 = 3
NUM_EMPLOYEES_CHOICE_5 = 4

NUM_EMPLOYEES_CHOICES = ((NUM_EMPLOYEES_CHOICE_1, '1-100'),
                         (NUM_EMPLOYEES_CHOICE_2, '100-500'),
                         (NUM_EMPLOYEES_CHOICE_3, '500-2000'),
                         (NUM_EMPLOYEES_CHOICE_4, '2000-5000'),
                         (NUM_EMPLOYEES_CHOICE_5, '> 5000'),)

HEARD_ABOUT_FROM_CHOICE_GOOGLE = 0
HEARD_ABOUT_FROM_CHOICE_BING = 1
HEARD_ABOUT_FROM_CHOICE_YAHOO = 2
HEARD_ABOUT_FROM_CHOICE_OTHER_SEARCH = 3
HEARD_ABOUT_FROM_CHOICE_NY_TIMES_PUBLICATION = 4
HEARD_ABOUT_FROM_CHOICE_RSA_SHOW = 5
HEARD_ABOUT_FROM_CHOICE_FRIEND = 6
HEARD_ABOUT_FROM_CHOICE_COLLEAGUE = 7
HEARD_ABOUT_FROM_CHOICE_PARTNER = 8
HEARD_ABOUT_FROM_CHOICE_EVENT = 9
HEARD_ABOUT_FROM_CHOICE_OTHER_PUBLICATION = 10
HEARD_ABOUT_FROM_CHOICE_OTHER = 11

HEARD_ABOUT_FROM_CHOICES = ((HEARD_ABOUT_FROM_CHOICE_GOOGLE, 'Google Search'),
                            (HEARD_ABOUT_FROM_CHOICE_BING, 'Bing Search'),
                            (HEARD_ABOUT_FROM_CHOICE_YAHOO, 'Yahoo Search'),
                            (HEARD_ABOUT_FROM_CHOICE_OTHER_SEARCH, 'Other Search Engine'),
                            (HEARD_ABOUT_FROM_CHOICE_NY_TIMES_PUBLICATION, 'NY Times Publication'),
                            (HEARD_ABOUT_FROM_CHOICE_RSA_SHOW, 'RSA Show'),
                            (HEARD_ABOUT_FROM_CHOICE_FRIEND, 'Friend'),
                            (HEARD_ABOUT_FROM_CHOICE_COLLEAGUE, 'Colleague'),
                            (HEARD_ABOUT_FROM_CHOICE_PARTNER, 'Partner'),
                            (HEARD_ABOUT_FROM_CHOICE_EVENT, 'Event'),
                            (HEARD_ABOUT_FROM_CHOICE_OTHER_PUBLICATION, 'Other Publication'),
                            (HEARD_ABOUT_FROM_CHOICE_OTHER, 'Other'),)

BUSINESS_TYPE_CHOICE_DISTRIBUTOR = 0
BUSINESS_TYPE_CHOICE_SYSTEMS_INTEGRATOR = 1
BUSINESS_TYPE_CHOICE_VALUE_ADDED_RESELLER = 2
BUSINESS_TYPE_CHOICE_OEM_PARTNER = 3
BUSINESS_TYPE_CHOICE_COMPUTERS = 4
BUSINESS_TYPE_CHOICE_SOFTWARE = 5
BUSINESS_TYPE_CHOICE_NETWORKING = 6
BUSINESS_TYPE_CHOICE_ACCOUNTING_SYSTEMS = 7
BUSINESS_TYPE_CHOICE_INVENTORY_CONTROL_SYSTEMS = 8
BUSINESS_TYPE_CHOICE_CRM_SYSTEMS = 9

BUSINESS_TYPE_CHOICES = ((BUSINESS_TYPE_CHOICE_DISTRIBUTOR, 'Distributor'),
                         (BUSINESS_TYPE_CHOICE_OEM_PARTNER, 'OEM Partner'),
                         (BUSINESS_TYPE_CHOICE_SYSTEMS_INTEGRATOR, 'Systems Integrator'),
                         (BUSINESS_TYPE_CHOICE_VALUE_ADDED_RESELLER, 'Value Added Reseller'),
                         )

TECHNOLOGY_BUSINESS_TYPE_CHOICES = ((BUSINESS_TYPE_CHOICE_ACCOUNTING_SYSTEMS, 'Accounting Systems'),
                                    (BUSINESS_TYPE_CHOICE_COMPUTERS, 'Computers'),
                                    (BUSINESS_TYPE_CHOICE_CRM_SYSTEMS, 'CRM Systems'),
                                    (BUSINESS_TYPE_CHOICE_INVENTORY_CONTROL_SYSTEMS, 'Inventory Control Systems'),
                                    (BUSINESS_TYPE_CHOICE_NETWORKING, 'Networking'),
                                    (BUSINESS_TYPE_CHOICE_SOFTWARE, 'Software'),
                                    )

TARGET_VERTICAL_FOCUS_CHOICE_AGRICULTURE = 0
TARGET_VERTICAL_FOCUS_CHOICE_BANKING_FINANCE = 1
TARGET_VERTICAL_FOCUS_CHOICE_BUSINESS_SERVICES = 2
TARGET_VERTICAL_FOCUS_CHOICE_GOVERNMENT = 3
TARGET_VERTICAL_FOCUS_CHOICE_HIGHER_EDUCATION = 4
TARGET_VERTICAL_FOCUS_CHOICE_K12_EDUCATION = 5
TARGET_VERTICAL_FOCUS_CHOICE_MANUFACTURING = 6
TARGET_VERTICAL_FOCUS_CHOICE_HEALTH_AND_MEDICAL = 7
TARGET_VERTICAL_FOCUS_CHOICE_OIL_GAS_CHEMICAL = 8
TARGET_VERTICAL_FOCUS_CHOICE_TRANSPORTATION = 9
TARGET_VERTICAL_FOCUS_CHOICE_RETAIL = 10
TARGET_VERTICAL_FOCUS_CHOICE_TELECOM = 11
TARGET_VERTICAL_FOCUS_CHOICE_UTILITIES = 12
TARGET_VERTICAL_FOCUS_CHOICE_WEB_SERVICES = 13
TARGET_VERTICAL_FOCUS_CHOICE_OTHER = 14

TARGET_VERTICAL_FOCUS_CHOICES = ((TARGET_VERTICAL_FOCUS_CHOICE_AGRICULTURE, 'Agriculture'),
                                 (TARGET_VERTICAL_FOCUS_CHOICE_BANKING_FINANCE, 'Banking / Finance'),
                                 (TARGET_VERTICAL_FOCUS_CHOICE_BUSINESS_SERVICES, 'Business Services'),
                                 (TARGET_VERTICAL_FOCUS_CHOICE_GOVERNMENT, 'Government'),
                                 (TARGET_VERTICAL_FOCUS_CHOICE_HIGHER_EDUCATION, 'Higher Education'),
                                 (TARGET_VERTICAL_FOCUS_CHOICE_K12_EDUCATION, 'K-12 Education'),
                                 (TARGET_VERTICAL_FOCUS_CHOICE_MANUFACTURING, 'Manufacturing'),
                                 (TARGET_VERTICAL_FOCUS_CHOICE_HEALTH_AND_MEDICAL, 'Health and Medical'),
                                 (TARGET_VERTICAL_FOCUS_CHOICE_OIL_GAS_CHEMICAL, 'Oil / Gas / Chemical'),
                                 (TARGET_VERTICAL_FOCUS_CHOICE_TRANSPORTATION, 'Transportation'),
                                 (TARGET_VERTICAL_FOCUS_CHOICE_RETAIL, 'Retail'),
                                 (TARGET_VERTICAL_FOCUS_CHOICE_TELECOM, 'Telecom'),
                                 (TARGET_VERTICAL_FOCUS_CHOICE_UTILITIES, 'Utilities'),
                                 (TARGET_VERTICAL_FOCUS_CHOICE_WEB_SERVICES, 'Web Services'),
                                 (TARGET_VERTICAL_FOCUS_CHOICE_OTHER, 'Other'),)

RESELL_TO_USA_FEDERAL_SECTOR_CHOICE_YES = 0
RESELL_TO_USA_FEDERAL_SECTOR_CHOICE_NO = 1
RESELL_TO_USA_FEDERAL_SECTOR_CHOICE_UNSURE = 2

RESELL_TO_USA_FEDERAL_SECTOR_CHOICES = ((RESELL_TO_USA_FEDERAL_SECTOR_CHOICE_YES, 'Yes'),
                                        (RESELL_TO_USA_FEDERAL_SECTOR_CHOICE_NO, 'No'),
                                        (RESELL_TO_USA_FEDERAL_SECTOR_CHOICE_UNSURE, 'Unsure'),)

OFFER_OWN_SUPPORT_CHOICE_24_7 = 0
OFFER_OWN_SUPPORT_CHOICE_8_5 = 1
OFFER_OWN_SUPPORT_CHOICE_NONE = 2

OFFER_OWN_SUPPORT_CHOICES = ((OFFER_OWN_SUPPORT_CHOICE_24_7, '24/7'),
                             (OFFER_OWN_SUPPORT_CHOICE_8_5, '8/5'),
                             (OFFER_OWN_SUPPORT_CHOICE_NONE, 'None'),)