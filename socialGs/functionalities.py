user_info_create = """
CREATE TABLE IF NOT EXISTS user_info (
    pk_id TEXT PRIMARY KEY,
    biography TEXT,
    follower_count INTEGER,
    following_count INTEGER,
    latitude REAL,
    longitude REAL,
    media_count INTEGER,
    has_exclusive_feed_content INTEGER,
    has_fan_club_subscriptions INTEGER,
    has_groups INTEGER,
    has_guides INTEGER,
    has_highlight_reels INTEGER,
    has_music_on_profile INTEGER,
    has_private_collections INTEGER,
    has_videos INTEGER,
    is_potential_business INTEGER,
    total_ar_effects INTEGER,
    total_clips_count INTEGER,
    total_igtv_videos INTEGER
    is_secondary_account_creation INTEGER,
    primary_profile_link_type INTEGER,
    show_fb_link_on_profile INTEGER,
    show_fb_page_link_on_profile INTEGER,
    can_hide_category INTEGER,
    smb_support_partner TEXT,
    current_catalog_id TEXT,
    mini_shop_seller_onboarding_status TEXT,
    account_category TEXT,
    can_add_fb_group_link_on_profile INTEGER,
    can_use_affiliate_partnership_messaging_as_creator INTEGER,
    can_use_affiliate_partnership_messaging_as_brand INTEGER,
    existing_user_age_collection_enabled INTEGER,
    fbid_v2 TEXT,
    feed_post_reshare_disabled INTEGER,
    full_name TEXT,
    has_public_tab_threads INTEGER,
    highlight_reshare_disabled INTEGER,
    include_direct_blacklist_status INTEGER,
    is_direct_roll_call_enabled INTEGER,
    is_new_to_instagram INTEGER,
    is_new_to_instagram_30d INTEGER,
    is_private INTEGER,
    profile_type INTEGER,
    show_account_transparency_details INTEGER,
    show_ig_app_switcher_badge INTEGER,
    show_post_insights_entry_point INTEGER,
    show_text_post_app_badge INTEGER,
    show_text_post_app_switcher_badge INTEGER,
    third_party_downloads_enabled INTEGER,
    strong_id__ TEXT,
    external_url TEXT,
    can_hide_public_contacts INTEGER,
    category TEXT,
    should_show_category INTEGER,
    category_id TEXT,
    is_category_tappable INTEGER,
    should_show_public_contacts INTEGER,
    is_eligible_for_smb_support_flow INTEGER,
    is_eligible_for_lead_center INTEGER,
    is_experienced_advertiser INTEGER,
    lead_details_app_id TEXT,
    is_business INTEGER,
    professional_conversion_suggested_account_type INTEGER,
    account_type INTEGER,
    direct_messaging TEXT,
    instagram_location_id TEXT,
    address_street TEXT,
    business_contact_method TEXT,
    city_id TEXT,
    city_name TEXT,
    contact_phone_number TEXT,
    is_profile_audio_call_enabled INTEGER,
    public_email TEXT,
    public_phone_country_code TEXT,
    public_phone_number TEXT,
    zip TEXT,
    displayed_action_button_partner TEXT,
    smb_delivery_partner TEXT,
    smb_support_delivery_partner TEXT,
    displayed_action_button_type TEXT,
    is_call_to_action_enabled INTEGER,
    num_of_admined_pages TEXT,
    page_id TEXT,
    page_name TEXT,
    ads_page_id TEXT,
    ads_page_name TEXT,
    shopping_post_onboard_nux_type TEXT,
    ads_incentive_expiration_date TEXT,
    FOREIGN KEY (pk_id) REFERENCES users(pk_id)
);
"""
def generate_user_info_insert_query(user_info):
    columns = ', '.join(user_info.keys())
    values = ', '.join([f"'{value}'" if isinstance(value, str) else str(value) for value in user_info.values()])
    
    insert_query = f"INSERT INTO user_info ({columns}) VALUES ({values});"
    
    return insert_query

def get_values_by_key(json_obj, target_key):
    results = []

    if isinstance(json_obj, dict):
        for key, value in json_obj.items():
            if key == target_key:
                results.append(value)
            else:
                results.extend(get_values_by_key(value, target_key))
    elif isinstance(json_obj, list):
        for item in json_obj:
            results.extend(get_values_by_key(item, target_key))
    return results
