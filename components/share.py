"""
Privacy-Focused Share Components
Enables sharing to Signal, Telegram, and other secure channels
"""

from dash import html, dcc, callback, Input, Output, State, clientside_callback
import dash_bootstrap_components as dbc
import urllib.parse


def create_share_button(share_id, content_type="page", custom_text=None):
    """
    Create a share button with privacy-focused options.

    Args:
        share_id: Unique ID for this share button instance
        content_type: Type of content being shared (page, alert, data, resource)
        custom_text: Optional custom text to share
    """
    return html.Div([
        dbc.Button(
            [html.Span("Share", className='share-btn-text')],
            id=f'share-btn-{share_id}',
            className='share-button',
            color='link',
            size='sm',
        ),
        dbc.Popover(
            [
                dbc.PopoverHeader("Share via Secure Channel"),
                dbc.PopoverBody([
                    html.Div([
                        # Signal
                        html.Button([
                            html.Span("Signal", className='channel-name'),
                        ], id=f'share-signal-{share_id}', className='share-channel-btn signal-btn'),

                        # Telegram
                        html.Button([
                            html.Span("Telegram", className='channel-name'),
                        ], id=f'share-telegram-{share_id}', className='share-channel-btn telegram-btn'),

                        # WhatsApp
                        html.Button([
                            html.Span("WhatsApp", className='channel-name'),
                        ], id=f'share-whatsapp-{share_id}', className='share-channel-btn whatsapp-btn'),

                        # Copy Link
                        html.Button([
                            html.Span("Copy Text", className='channel-name'),
                        ], id=f'share-copy-{share_id}', className='share-channel-btn copy-btn'),

                        # Email (E2EE options exist)
                        html.Button([
                            html.Span("Email", className='channel-name'),
                        ], id=f'share-email-{share_id}', className='share-channel-btn email-btn'),
                    ], className='share-channels'),

                    html.Div([
                        html.Small(
                            "Signal & Telegram offer end-to-end encryption",
                            className='security-note'
                        ),
                    ], className='share-footer'),
                ]),
            ],
            id=f'share-popover-{share_id}',
            target=f'share-btn-{share_id}',
            trigger='click',
            placement='bottom',
        ),
        # Hidden store for share content
        dcc.Store(id=f'share-content-{share_id}', data={
            'type': content_type,
            'custom_text': custom_text,
        }),
        # Clipboard component
        dcc.Clipboard(id=f'clipboard-{share_id}', style={'display': 'none'}),
    ], className='share-container')


def create_alert_share_widget():
    """
    Create a dedicated widget for sharing ICE activity alerts.
    Designed for quick community alerts via Signal.
    """
    return html.Div([
        html.Div([
            html.H4("Community Alert", className='alert-widget-title'),
            html.P("Share ICE activity information securely", className='alert-widget-subtitle'),
        ], className='alert-widget-header'),

        # Quick alert templates
        html.Div([
            dbc.Textarea(
                id='alert-message-input',
                placeholder='Describe the activity (location, time, vehicle description, etc.)',
                className='alert-textarea',
                rows=3,
            ),

            html.Div([
                dbc.Select(
                    id='alert-type-select',
                    options=[
                        {'label': 'ICE Vehicle Sighting', 'value': 'vehicle'},
                        {'label': 'Enforcement Activity', 'value': 'enforcement'},
                        {'label': 'Checkpoint', 'value': 'checkpoint'},
                        {'label': 'Raid/Operation', 'value': 'raid'},
                        {'label': 'Other Activity', 'value': 'other'},
                    ],
                    value='vehicle',
                    className='alert-type-select',
                ),
                dbc.Input(
                    id='alert-location-input',
                    placeholder='Location (city, intersection, etc.)',
                    className='alert-location-input',
                ),
            ], className='alert-inputs-row'),

            html.Div([
                html.Button([
                    "Share via Signal"
                ], id='quick-signal-share', className='quick-share-btn signal-btn'),
                html.Button([
                    "Copy Alert"
                ], id='quick-copy-alert', className='quick-share-btn copy-btn'),
            ], className='alert-actions'),

            html.Div(id='alert-share-feedback', className='alert-feedback'),
        ], className='alert-widget-body'),

        html.Div([
            html.Small([
                "Your privacy matters. This tool doesn't store or transmit your messages. ",
                "All sharing happens directly through your chosen app."
            ], className='privacy-note'),
        ], className='alert-widget-footer'),

        dcc.Clipboard(id='alert-clipboard', style={'display': 'none'}),
    ], className='alert-share-widget')


def get_share_content(content_type, page_title=None, custom_data=None):
    """
    Generate shareable content based on type.

    Returns dict with 'text' and 'url' keys.
    """
    base_url = "https://ice-data-explorer.onrender.com"  # Update with actual URL

    templates = {
        'page': {
            'text': f"ICE Enforcement Data: {page_title or 'The Cost of Enforcement'}\n\n"
                   f"Interactive investigation into U.S. immigration detention & deportation.\n\n"
                   f"{base_url}",
            'url': base_url,
        },
        'alert': {
            'text': "COMMUNITY ALERT - ICE Activity Reported\n\n"
                   f"{custom_data.get('message', '') if custom_data else ''}\n"
                   f"Type: {custom_data.get('type', 'Unknown') if custom_data else 'Unknown'}\n"
                   f"Location: {custom_data.get('location', 'Not specified') if custom_data else 'Not specified'}\n\n"
                   "Know Your Rights: https://www.aclu.org/know-your-rights/immigrants-rights\n"
                   "Report: https://unitedwedream.org/protect",
            'url': None,
        },
        'stat': {
            'text': f"ICE Data Point:\n\n{custom_data.get('stat', '') if custom_data else ''}\n\n"
                   f"Source: {base_url}",
            'url': base_url,
        },
        'resource': {
            'text': f"Immigration Resource:\n\n{custom_data.get('name', '') if custom_data else ''}\n"
                   f"{custom_data.get('url', '') if custom_data else ''}\n\n"
                   f"More resources: {base_url}/resources",
            'url': custom_data.get('url') if custom_data else base_url,
        },
    }

    return templates.get(content_type, templates['page'])


def generate_signal_url(text):
    """
    Generate a Signal share URL.
    Note: Signal doesn't have a universal share URL, so we provide
    instructions and copy functionality.
    """
    # Signal doesn't support direct web sharing URLs
    # Return None to indicate clipboard should be used
    return None


def generate_telegram_url(text, url=None):
    """Generate Telegram share URL."""
    encoded_text = urllib.parse.quote(text)
    if url:
        encoded_url = urllib.parse.quote(url)
        return f"https://t.me/share/url?url={encoded_url}&text={encoded_text}"
    return f"https://t.me/share/url?text={encoded_text}"


def generate_whatsapp_url(text):
    """Generate WhatsApp share URL."""
    encoded_text = urllib.parse.quote(text)
    return f"https://wa.me/?text={encoded_text}"


def generate_email_url(subject, body):
    """Generate mailto URL."""
    encoded_subject = urllib.parse.quote(subject)
    encoded_body = urllib.parse.quote(body)
    return f"mailto:?subject={encoded_subject}&body={encoded_body}"


# Clientside JavaScript for share functionality
SHARE_JS = """
window.dashShareUtils = {
    copyToClipboard: function(text) {
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(text).then(function() {
                return true;
            }).catch(function(err) {
                console.error('Clipboard write failed:', err);
                return false;
            });
        } else {
            // Fallback for older browsers
            var textarea = document.createElement('textarea');
            textarea.value = text;
            textarea.style.position = 'fixed';
            textarea.style.opacity = '0';
            document.body.appendChild(textarea);
            textarea.select();
            try {
                document.execCommand('copy');
                document.body.removeChild(textarea);
                return true;
            } catch (err) {
                document.body.removeChild(textarea);
                return false;
            }
        }
    },

    openSignalShare: function(text) {
        // Copy to clipboard and show instruction
        this.copyToClipboard(text);

        // Try to open Signal app (works on mobile/desktop with Signal installed)
        // signal:// URL scheme for direct messaging
        var signalUrl = 'signal://send?text=' + encodeURIComponent(text);

        // Create a hidden iframe to try the URL scheme
        var iframe = document.createElement('iframe');
        iframe.style.display = 'none';
        iframe.src = signalUrl;
        document.body.appendChild(iframe);

        // Clean up after attempt
        setTimeout(function() {
            document.body.removeChild(iframe);
        }, 1000);

        return true;
    },

    showShareFeedback: function(elementId, message) {
        var el = document.getElementById(elementId);
        if (el) {
            el.textContent = message;
            el.classList.add('visible');
            setTimeout(function() {
                el.classList.remove('visible');
            }, 3000);
        }
    }
};
"""
