<!DOCTYPE html><!-- Last Published: Wed Feb 04 2026 13:27:16 GMT+0000 (Coordinated Universal Time) --><html data-wf-domain="www.orbcomm.com" data-wf-page="6904e526a81cf6a05bbae225" data-wf-site="6904e526a81cf6a05bbae250" lang="en"><head><meta charset="utf-8"/><title>ORBCOMM</title><link rel="alternate" hrefLang="x-default" href="https://www.orbcomm.com/"/><link rel="alternate" hrefLang="en" href="https://www.orbcomm.com/"/><link rel="alternate" hrefLang="es" href="https://www.orbcomm.com/es"/><link rel="alternate" hrefLang="pt" href="https://www.orbcomm.com/pt"/><meta content="https://cdn.prod.website-files.com/6904e526a81cf6a05bbae250/6904eec734c035e7649943e3_OG%20share%20image.png" property="og:image"/><meta content="width=device-width, initial-scale=1" name="viewport"/><link href="https://cdn.prod.website-files.com/6904e526a81cf6a05bbae250/css/orbcomm-staging.shared.44029b71c.min.css" rel="stylesheet" type="text/css" integrity="sha384-RAKbccJP5BAA9EQTnZCKe/+0popTxrC6IuBGGXXEYGCUfb7R8NkrA+nqP4/fV+pd" crossorigin="anonymous"/><script type="text/javascript">!function(o,c){var n=c.documentElement,t=" w-mod-";n.className+=t+"js",("ontouchstart"in o||o.DocumentTouch&&c instanceof DocumentTouch)&&(n.className+=t+"touch")}(window,document);</script><link href="https://cdn.prod.website-files.com/6904e526a81cf6a05bbae250/6904ee5771126bc6b9d70f9d_Favicon%2032x32.png" rel="shortcut icon" type="image/x-icon"/><link href="https://cdn.prod.website-files.com/6904e526a81cf6a05bbae250/6904ee5ad9cdc5884ad489fa_Webclip%20256%20x%20256.png" rel="apple-touch-icon"/><link href="https://www.orbcomm.com" rel="canonical"/><!-- Google Tag Manager -->
<script>
(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','GTM-5KQ6KB');
</script>
<!-- End Google Tag Manager -->



<style>

/* 
Button highlight animation:
This CSS creates a light reflection (shine) effect that moves across the button on hover.
Two pseudo-elements (::before and ::after) are used as diagonal light streaks,
which slide from left to right when the user hovers over the button.
The transform and skewX values control the angle and movement of the light.
*/
.button {
  position: relative;

  /*color: #fff;*/
  overflow: hidden;
}

.button::before,
.button::after {
  height: 100%;
  position: absolute;
  top: 0;
  left: 0;
  transform: translateX(-100px) skewX(-15deg);
  content: "";
  transition: all 0.9s ease;
}

.button::before {
  width: 60px;
  background: rgba(255, 255, 255, 0.5);
  filter: blur(30px);
  opacity: 0.5;
}

.button::after {
  width: 30px;
  left: 30px;
  background: rgba(255, 255, 255, 0.2);
  filter: blur(5px);
}

.button:hover::before,
.button:hover::after {
  transform: translateX(400px) skewX(-15deg);
}

/* 📱 Mobile adjustments */
@media (max-width: 768px) {
  .button::before,
  .button::after {
    transform: translateX(-50vw) skewX(-15deg);
  }

  .button:hover::before,
  .button:hover::after {
    transform: translateX(120vw) skewX(-15deg);
  }
}
</style><style>
[data-reveal="bottom"] {
  display: inline-block;
  overflow: hidden;
}

[data-reveal="bottom"] .reveal-line {
  display: block;
  overflow: hidden;
}

[data-reveal="bottom"] .reveal-line span {
  display: inline-block;
  transform: translateY(100%);
  opacity: 0;
}
</style></head><body class="body is-dots"><div class="page-wrapper"><div class="global-styles w-embed"><style>

/* Make text look crisper and more legible in all browsers */
body {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}

/* Focus state style for keyboard navigation for the focusable elements */
*[tabindex]:focus-visible,
  input[type="file"]:focus-visible {
   outline: 0.125rem solid #4d65ff;
   outline-offset: 0.125rem;
}

/* Set color style to inherit */
.inherit-color * {
    color: inherit;
}

/* Get rid of top margin on first element in any rich text element */
.w-richtext > :not(div):first-child, .w-richtext > div:first-child > :first-child {
  margin-top: 0 !important;
}

/* Get rid of bottom margin on last element in any rich text element */
.w-richtext>:last-child, .w-richtext ol li:last-child, .w-richtext ul li:last-child {
	margin-bottom: 0 !important;
}


/* Make sure containers never lose their center alignment */
.container-medium,.container-small, .container-large {
	margin-right: auto !important;
  margin-left: auto !important;
}

/* 
Make the following elements inherit typography styles from the parent and not have hardcoded values. 
Important: You will not be able to style for example "All Links" in Designer with this CSS applied.
Uncomment this CSS to use it in the project. Leave this message for future hand-off.
*/
/*
a,
.w-input,
.w-select,
.w-tab-link,
.w-nav-link,
.w-dropdown-btn,
.w-dropdown-toggle,
.w-dropdown-link {
  color: inherit;
  text-decoration: inherit;
  font-size: inherit;
}
*/

/* Apply "..." after 3 lines of text */
.text-style-3lines {
	display: -webkit-box;
	overflow: hidden;
	-webkit-line-clamp: 3;
	-webkit-box-orient: vertical;
}

/* Apply "..." after 2 lines of text */
.text-style-2lines {
	display: -webkit-box;
	overflow: hidden;
	-webkit-line-clamp: 2;
	-webkit-box-orient: vertical;
}

/* Adds inline flex display */
.display-inlineflex {
  display: inline-flex;
}

/* These classes are never overwritten */
.hide {
  display: none !important;
}

@media screen and (max-width: 991px) {
    .hide, .hide-tablet {
        display: none !important;
    }
}
  @media screen and (max-width: 767px) {
    .hide-mobile-landscape{
      display: none !important;
    }
}
  @media screen and (max-width: 479px) {
    .hide-mobile{
      display: none !important;
    }
}
 
.margin-0 {
  margin: 0rem !important;
}
  
.padding-0 {
  padding: 0rem !important;
}

.spacing-clean {
padding: 0rem !important;
margin: 0rem !important;
}

.margin-top {
  margin-right: 0rem !important;
  margin-bottom: 0rem !important;
  margin-left: 0rem !important;
}

.padding-top {
  padding-right: 0rem !important;
  padding-bottom: 0rem !important;
  padding-left: 0rem !important;
}
  
.margin-right {
  margin-top: 0rem !important;
  margin-bottom: 0rem !important;
  margin-left: 0rem !important;
}

.padding-right {
  padding-top: 0rem !important;
  padding-bottom: 0rem !important;
  padding-left: 0rem !important;
}

.margin-bottom {
  margin-top: 0rem !important;
  margin-right: 0rem !important;
  margin-left: 0rem !important;
}

.padding-bottom {
  padding-top: 0rem !important;
  padding-right: 0rem !important;
  padding-left: 0rem !important;
}

.margin-left {
  margin-top: 0rem !important;
  margin-right: 0rem !important;
  margin-bottom: 0rem !important;
}
  
.padding-left {
  padding-top: 0rem !important;
  padding-right: 0rem !important;
  padding-bottom: 0rem !important;
}
  
.margin-horizontal {
  margin-top: 0rem !important;
  margin-bottom: 0rem !important;
}

.padding-horizontal {
  padding-top: 0rem !important;
  padding-bottom: 0rem !important;
}

.margin-vertical {
  margin-right: 0rem !important;
  margin-left: 0rem !important;
}
  
.padding-vertical {
  padding-right: 0rem !important;
  padding-left: 0rem !important;
}

</style></div><nav data-wf--navbar--variant="base" class="nav"><div class="nav_container"><a aria-label="ORBCOMM home" href="/" aria-current="page" class="nav_logo-link w-inline-block w--current"><img src="https://cdn.prod.website-files.com/6904e526a81cf6a05bbae250/6943e5cec082acd30eb7cece_ORBCOMM%20logo%202018%20color%201.avif" loading="lazy" sizes="100vw" srcset="https://cdn.prod.website-files.com/6904e526a81cf6a05bbae250/6943e5cec082acd30eb7cece_ORBCOMM%20logo%202018%20color%201-p-500.png 500w, https://cdn.prod.website-files.com/6904e526a81cf6a05bbae250/6943e5cec082acd30eb7cece_ORBCOMM%20logo%202018%20color%201.avif 816w" alt="Orbcomm logo" class="nav_logo"/><img src="https://cdn.prod.website-files.com/6904e526a81cf6a05bbae250/6943e77e0f1eb6b2b21d00e6_Orbcomm_logo%202.png" loading="lazy" sizes="100vw" srcset="https://cdn.prod.website-files.com/6904e526a81cf6a05bbae250/6943e77e0f1eb6b2b21d00e6_Orbcomm_logo%202-p-500.png 500w, https://cdn.prod.website-files.com/6904e526a81cf6a05bbae250/6943e77e0f1eb6b2b21d00e6_Orbcomm_logo%202.png 768w" alt="Orbcomm logo" class="nav_logo is-light"/></a><div class="nav_menu-wrap"><div class="nav_menu"><a href="/about-us" class="nav_link w-inline-block"><div>About</div></a><a href="/careers" class="nav_link w-inline-block"><div>Careers</div></a><a href="/newsroom" class="nav_link w-inline-block"><div>Newsroom</div></a></div></div><div class="lang-wrapp"><div data-hover="true" data-delay="0" class="lang-drop w-dropdown"><div class="lang-drop-toggle w-dropdown-toggle"><div class="lang-drop-icon w-icon-dropdown-toggle"></div><div>EN</div></div><nav class="lang-drop-nav w-dropdown-list"><div class="navbar-drop-nav"><div class="w-locales-list"><div role="list" class="w-locales-items"><div role="listitem" class="locale w-locales-item"><a hreflang="en" href="/" aria-current="page" class="navbar-drop-link w--current">EN</a></div><div role="listitem" class="locale w-locales-item"><a hreflang="es" href="/es" class="navbar-drop-link">ES</a></div><div role="listitem" class="locale w-locales-item"><a hreflang="pt" href="/pt" class="navbar-drop-link">PT</a></div></div></div></div></nav></div><div class="nav-menu-button"><div class="nav-menu-line first dark"></div><div class="nav-menu-line mid dark"></div><div class="nav-menu-line last dark"></div></div></div></div></nav><div class="w-embed"><style>
.card_bg-overlay {
	background: linear-gradient(0deg, rgba(2, 18, 46, 0) 0%, #02122E 90%);
}
.card_bg-overlay.is-dark {
	background: linear-gradient(0deg, rgba(23, 10, 7, 0) 0%, #170A07 90%);
}
</style></div><main class="relative-big"><section class="section"><div class="padding-out"><div class="container-xlarge"><div class="padding-global"><div class="home-quote"><h1 data-reveal="bottom" class="h1-56px text-weight-medium text-color-red spec">Where IoT powers asset intelligence</h1><div data-wf--spacer--variant="12px" class="spacer w-variant-67cb0169-0bbe-da82-60a5-ea4cef1a957b"></div><div class="max-width-700"><p data-reveal="bottom" class="paragraph text-color-gray-800">ORBCOMM’s purpose-built brands make the world safer and more sustainable by providing intelligent visibility across our customers’ operations.</p></div><div data-wf--spacer--variant="24px" class="spacer w-variant-c6b355e9-04b0-086a-d92a-ee1c39d8640e hide"></div><div id="" class="home-grid hide"><dl data-animate="slide-up" id="" class="margin-0"><dt class="h1 text-weight-normal mob-lg">30+</dt><div data-wf--spacer--variant="4px" class="spacer"></div><dd class="flex-h-center mob-center gap-sm"><div class="button-icon w-embed"><svg width="100%" height="100%" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M3.84922 8.61912C3.70326 7.96165 3.72567 7.27796 3.91437 6.63146C4.10308 5.98496 4.45196 5.39657 4.92868 4.92084C5.40541 4.44512 5.99453 4.09747 6.64142 3.91012C7.28832 3.72277 7.97205 3.70179 8.62922 3.84912C8.99093 3.28342 9.48922 2.81788 10.0782 2.49541C10.6671 2.17293 11.3278 2.00391 11.9992 2.00391C12.6707 2.00391 13.3313 2.17293 13.9203 2.49541C14.5092 2.81788 15.0075 3.28342 15.3692 3.84912C16.0274 3.70114 16.7123 3.72203 17.3602 3.90983C18.0081 4.09764 18.598 4.44626 19.0751 4.92327C19.5521 5.40029 19.9007 5.99019 20.0885 6.63812C20.2763 7.28605 20.2972 7.97095 20.1492 8.62912C20.7149 8.99083 21.1805 9.48912 21.5029 10.0781C21.8254 10.667 21.9944 11.3277 21.9944 11.9991C21.9944 12.6706 21.8254 13.3312 21.5029 13.9202C21.1805 14.5091 20.7149 15.0074 20.1492 15.3691C20.2966 16.0263 20.2756 16.71 20.0882 17.3569C19.9009 18.0038 19.5532 18.5929 19.0775 19.0697C18.6018 19.5464 18.0134 19.8953 17.3669 20.084C16.7204 20.2727 16.0367 20.2951 15.3792 20.1491C15.018 20.717 14.5193 21.1845 13.9293 21.5084C13.3394 21.8324 12.6772 22.0022 12.0042 22.0022C11.3312 22.0022 10.669 21.8324 10.0791 21.5084C9.48914 21.1845 8.99045 20.717 8.62922 20.1491C7.97205 20.2965 7.28832 20.2755 6.64142 20.0881C5.99453 19.9008 5.40541 19.5531 4.92868 19.0774C4.45196 18.6017 4.10308 18.0133 3.91437 17.3668C3.72567 16.7203 3.70326 16.0366 3.84922 15.3791C3.27917 15.0184 2.80963 14.5193 2.48426 13.9283C2.1589 13.3374 1.98828 12.6737 1.98828 11.9991C1.98828 11.3245 2.1589 10.6609 2.48426 10.0699C2.80963 9.47895 3.27917 8.97988 3.84922 8.61912Z" stroke="#BA0C2F" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M11.1225 7.69005C11.1886 7.48739 11.3177 7.31114 11.491 7.18702C11.6643 7.0629 11.8727 6.9974 12.0858 7.00008C12.299 7.00276 12.5057 7.07348 12.6758 7.20192C12.8459 7.33035 12.9706 7.50979 13.0315 7.71405L13.7685 9.16605C13.8402 9.30721 13.9445 9.42931 14.0726 9.52232C14.2007 9.61533 14.3491 9.67659 14.5055 9.70105L16.1395 9.95705C16.3499 9.95788 16.5547 10.025 16.7247 10.149C16.8948 10.273 17.0213 10.4474 17.0865 10.6475C17.1516 10.8475 17.152 11.0631 17.0875 11.2634C17.0231 11.4636 16.8971 11.6385 16.7275 11.7631L15.5555 12.9311C15.4433 13.0428 15.3592 13.1795 15.3102 13.3301C15.2612 13.4806 15.2486 13.6407 15.2735 13.7971L15.5325 15.4101C15.6038 15.6122 15.6082 15.8319 15.5451 16.0368C15.482 16.2417 15.3547 16.4208 15.1821 16.5479C15.0094 16.6749 14.8005 16.7431 14.5862 16.7424C14.3718 16.7418 14.1633 16.6722 13.9915 16.5441L12.5265 15.7941C12.3854 15.7217 12.2291 15.684 12.0705 15.684C11.9119 15.684 11.7556 15.7217 11.6145 15.7941L10.1495 16.5441C9.9777 16.6711 9.76968 16.7399 9.55597 16.7401C9.34225 16.7403 9.13408 16.6721 8.96197 16.5454C8.78987 16.4187 8.66288 16.2402 8.59963 16.036C8.53638 15.8319 8.5402 15.6129 8.61052 15.4111L8.86852 13.7981C8.89359 13.6415 8.8811 13.4813 8.83207 13.3305C8.78304 13.1798 8.69888 13.0429 8.58652 12.9311L7.43052 11.7791C7.25517 11.6576 7.12327 11.4832 7.05407 11.2814C6.98488 11.0797 6.98202 10.861 7.04591 10.6575C7.1098 10.454 7.2371 10.2763 7.40921 10.1502C7.58131 10.0242 7.78921 9.95652 8.00252 9.95705L9.63552 9.70105C9.79194 9.67659 9.94033 9.61533 10.0685 9.52232C10.1966 9.42931 10.3008 9.30721 10.3725 9.16605L11.1225 7.69005Z" stroke="#BA0C2F" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg></div><div class="home_block">Years of industrial IoT experience</div></dd></dl><dl data-animate="slide-up" id="" class="margin-0"><dt class="h1 text-weight-normal mob-lg">2.9M+</dt><div data-wf--spacer--variant="4px" class="spacer"></div><dd class="flex-h-center mob-center gap-sm"><div class="button-icon w-embed"><svg width="100%" height="100%" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M16.2461 7.76562C17.3691 8.89055 17.9998 10.4151 17.9998 12.0046C17.9998 13.5941 17.3691 15.1187 16.2461 16.2436" stroke="#BA0C2F" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M19.0742 4.9375C20.9471 6.81253 21.9991 9.35433 21.9991 12.0045C21.9991 14.6547 20.9471 17.1965 19.0742 19.0715" stroke="#BA0C2F" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M4.92487 19.0715C3.05199 17.1965 2 14.6547 2 12.0045C2 9.35433 3.05199 6.81253 4.92487 4.9375" stroke="#BA0C2F" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M7.75372 16.2436C6.63073 15.1187 6 13.5941 6 12.0046C6 10.4151 6.63073 8.89055 7.75372 7.76562" stroke="#BA0C2F" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M12 14C13.1046 14 14 13.1046 14 12C14 10.8954 13.1046 10 12 10C10.8954 10 10 10.8954 10 12C10 13.1046 10.8954 14 12 14Z" stroke="#BA0C2F" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg></div><div class="home_block">Connected devices worldwide</div></dd></dl></div></div></div></div></div></section><div class="wrapper"><section class="section"><div class="padding-out"><div class="container-large"><div class="padding-global"><div data-animate="slide-up" class="flex-h-center mob-center hide"><div class="eyebrow"><div class="button-icon is-sm w-embed"><svg width="100%" height="100%" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M1.42226 3.03072C2.53625 1.44611 4.29983 0.407728 6.17191 0.0859375C6.17588 0.971537 6.17323 1.85713 6.17455 2.74409C4.75892 3.10644 3.51396 4.13536 2.94374 5.51716C2.097 7.43844 2.69501 9.88431 4.33291 11.1674C5.95096 12.5235 8.46734 12.5492 10.1052 11.2134C10.9467 10.5576 11.5354 9.60173 11.804 8.56065C12.6745 8.54848 13.5451 8.55659 14.4156 8.55524C14.1603 9.9776 13.561 11.3499 12.5859 12.4086C11.3661 13.7864 9.6144 14.6706 7.79789 14.7896C5.92582 14.9843 4.0048 14.3258 2.57461 13.0887C1.14707 11.8705 0.210375 10.0722 0.0304438 8.17937C-0.129642 6.36896 0.342679 4.48689 1.42226 3.03072Z" fill="#0D0A07"/>
<path d="M7.22984 0C9.21834 0.00135206 11.1896 0.861263 12.5404 2.35664C13.7907 3.70735 14.4945 5.55291 14.4998 7.41064C13.6465 7.41064 12.7945 7.41064 11.9411 7.41064C11.9107 6.04776 11.3378 4.6957 10.3151 3.8074C9.47236 3.03943 8.35044 2.64733 7.22852 2.61759C7.22852 1.74416 7.22852 0.872078 7.22984 0Z" fill="#BA0C2F"/>
<path d="M7.2305 3.76562C8.28098 3.79402 9.32219 4.26994 9.98238 5.11633C10.5116 5.75451 10.7643 6.58197 10.8013 7.40807C10.2351 7.40943 9.66883 7.41078 9.1039 7.40807C9.07479 6.38862 8.2307 5.52195 7.2305 5.50167C7.22785 4.92299 7.22785 4.34431 7.2305 3.76562Z" fill="#BA0C2F"/>
<path d="M6.92 6.4971C7.59078 6.22533 8.35548 6.93111 8.1557 7.64094C8.03266 8.33319 7.1039 8.6374 6.60248 8.15472C6.04813 7.70719 6.24129 6.6972 6.92 6.4971Z" fill="#BA0C2F"/>
</svg></div><h2 class="large-paragraph text-weight-semibold">ORBCOMM brands</h2></div></div><div data-wf--spacer--variant="32px" class="spacer w-variant-c9c1a8c1-69e6-c5b9-4c77-64c6fb4de155 hide"></div><div class="grid-2x"><article data-hover="lift" data-animate="slide-up" class="card"><div class="card_btn no-auto small"><div class="large-paragraph text-weight-medium">Get started with VIACHAIN</div><div class="button-icon mob-sm w-embed"><svg width="100%" height="100%" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M21 13V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H11" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M21 3L12 12" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M15 3H21V9" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg></div></div><div data-wf--spacer--variant="16px" class="spacer w-variant-c0c4192d-9f2f-dfe5-bb36-40529c81f933"></div><h3 class="h5">Intelligent cargo visibility that pays for itself</h3><div data-wf--spacer--variant="8px" class="spacer w-variant-33024a05-ce6e-0de0-0914-7da82612e4ce"></div><p class="paragraph text-color-gray-300 z-index-3">Transform blind spots into insights. Reduce spoilage, combat cargo theft and simplify compliance with the industry leader in supply chain IoT.</p><div data-wf--spacer--variant="24px" class="spacer w-variant-c6b355e9-04b0-086a-d92a-ee1c39d8640e"></div><div data-poster-url="https://cdn.prod.website-files.com/6900a481c2fcf73a832a3989%2F6905272c0439dabaf5f89b75_VIACHAIN%20-%20V03-poster-00001.jpg" data-video-urls="https://cdn.prod.website-files.com/6900a481c2fcf73a832a3989%2F6905272c0439dabaf5f89b75_VIACHAIN%20-%20V03-transcode.mp4,https://cdn.prod.website-files.com/6900a481c2fcf73a832a3989%2F6905272c0439dabaf5f89b75_VIACHAIN%20-%20V03-transcode.webm" data-autoplay="true" data-loop="true" data-wf-ignore="true" class="card_bg-img w-background-video w-background-video-atom"><video id="169d8cf4-40de-7d44-e931-ddb76c509481-video" autoplay="" loop="" style="background-image:url(&quot;https://cdn.prod.website-files.com/6900a481c2fcf73a832a3989%2F6905272c0439dabaf5f89b75_VIACHAIN%20-%20V03-poster-00001.jpg&quot;)" muted="" playsinline="" data-wf-ignore="true" data-object-fit="cover"><source src="https://cdn.prod.website-files.com/6900a481c2fcf73a832a3989%2F6905272c0439dabaf5f89b75_VIACHAIN%20-%20V03-transcode.mp4" data-wf-ignore="true"/><source src="https://cdn.prod.website-files.com/6900a481c2fcf73a832a3989%2F6905272c0439dabaf5f89b75_VIACHAIN%20-%20V03-transcode.webm" data-wf-ignore="true"/></video></div><div class="card_bg-overlay"></div><a aria-label="Learn more about VIACHAIN" href="https://www.viachain.io/" target="_blank" class="card_link w-inline-block"></a><div class="margin-top margine-auto"><img src="https://cdn.prod.website-files.com/6904e526a81cf6a05bbae250/696681b0c6e2e7f1a6a68fc6_viachain.avif" loading="lazy" alt="Viachain Logo
" class="card_logo z-index-3"/></div></article><article data-hover="lift" data-animate="slide-up" class="card is-dark"><div class="card_btn is-red no-auto small"><div class="large-paragraph text-weight-medium">Get started with SKYWAVE</div><div class="button-icon mob-sm w-embed"><svg width="100%" height="100%" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M21 13V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H11" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M21 3L12 12" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M15 3H21V9" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg></div></div><div data-wf--spacer--variant="16px" class="spacer w-variant-c0c4192d-9f2f-dfe5-bb36-40529c81f933"></div><h3 class="h5">Launch industrial IoT solutions in weeks, not years</h3><div data-wf--spacer--variant="8px" class="spacer w-variant-33024a05-ce6e-0de0-0914-7da82612e4ce"></div><p class="large-paragraph text-color-gray-300 z-index-3">Build and scale with hybrid satellite-cellular connectivity and advanced direct-to-device capabilities. Global. Reliable. Always connected.</p><div data-poster-url="https://cdn.prod.website-files.com/6904e526a81cf6a05bbae250%2F6908a8e2ae3ed531ea08f00a_68dd23291f3e31aab6165aab_690382235cfb8dc6b8012259_Skywave%20homepage%20video%20%281%29-transcode-poster-00001.jpg" data-video-urls="https://cdn.prod.website-files.com/6904e526a81cf6a05bbae250%2F6908a8e2ae3ed531ea08f00a_68dd23291f3e31aab6165aab_690382235cfb8dc6b8012259_Skywave%20homepage%20video%20%281%29-transcode-transcode.mp4,https://cdn.prod.website-files.com/6904e526a81cf6a05bbae250%2F6908a8e2ae3ed531ea08f00a_68dd23291f3e31aab6165aab_690382235cfb8dc6b8012259_Skywave%20homepage%20video%20%281%29-transcode-transcode.webm" data-autoplay="true" data-loop="true" data-wf-ignore="true" class="card_bg-img w-background-video w-background-video-atom"><video id="db2bc70f-0958-c427-463a-7d7bf0c65da6-video" autoplay="" loop="" style="background-image:url(&quot;https://cdn.prod.website-files.com/6904e526a81cf6a05bbae250%2F6908a8e2ae3ed531ea08f00a_68dd23291f3e31aab6165aab_690382235cfb8dc6b8012259_Skywave%20homepage%20video%20%281%29-transcode-poster-00001.jpg&quot;)" muted="" playsinline="" data-wf-ignore="true" data-object-fit="cover"><source src="https://cdn.prod.website-files.com/6904e526a81cf6a05bbae250%2F6908a8e2ae3ed531ea08f00a_68dd23291f3e31aab6165aab_690382235cfb8dc6b8012259_Skywave%20homepage%20video%20%281%29-transcode-transcode.mp4" data-wf-ignore="true"/><source src="https://cdn.prod.website-files.com/6904e526a81cf6a05bbae250%2F6908a8e2ae3ed531ea08f00a_68dd23291f3e31aab6165aab_690382235cfb8dc6b8012259_Skywave%20homepage%20video%20%281%29-transcode-transcode.webm" data-wf-ignore="true"/></video></div><div class="card_bg-overlay is-dark"></div><a aria-label="Learn more about SKYWAVE" href="https://www.skywave.com/" target="_blank" class="card_link w-inline-block"></a><div class="margin-top margine-auto"><img src="https://cdn.prod.website-files.com/6904e526a81cf6a05bbae250/696681b063513e35c55ea6cf_skywave.avif" loading="lazy" alt="Skywave logo" class="card_logo z-index-3"/></div></article></div><div data-wf--spacer--variant="56px" class="spacer w-variant-6a81755c-3837-d04d-30e7-c056d0a9f5b6"></div></div></div></div></section><div id="" class="home-grid bottom"><dl data-animate="slide-up" id="" class="margin-0"><div class="button-icon w-embed"><svg width="100%" height="100%" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M3.84922 8.61912C3.70326 7.96165 3.72567 7.27796 3.91437 6.63146C4.10308 5.98496 4.45196 5.39657 4.92868 4.92084C5.40541 4.44512 5.99453 4.09747 6.64142 3.91012C7.28832 3.72277 7.97205 3.70179 8.62922 3.84912C8.99093 3.28342 9.48922 2.81788 10.0782 2.49541C10.6671 2.17293 11.3278 2.00391 11.9992 2.00391C12.6707 2.00391 13.3313 2.17293 13.9203 2.49541C14.5092 2.81788 15.0075 3.28342 15.3692 3.84912C16.0274 3.70114 16.7123 3.72203 17.3602 3.90983C18.0081 4.09764 18.598 4.44626 19.0751 4.92327C19.5521 5.40029 19.9007 5.99019 20.0885 6.63812C20.2763 7.28605 20.2972 7.97095 20.1492 8.62912C20.7149 8.99083 21.1805 9.48912 21.5029 10.0781C21.8254 10.667 21.9944 11.3277 21.9944 11.9991C21.9944 12.6706 21.8254 13.3312 21.5029 13.9202C21.1805 14.5091 20.7149 15.0074 20.1492 15.3691C20.2966 16.0263 20.2756 16.71 20.0882 17.3569C19.9009 18.0038 19.5532 18.5929 19.0775 19.0697C18.6018 19.5464 18.0134 19.8953 17.3669 20.084C16.7204 20.2727 16.0367 20.2951 15.3792 20.1491C15.018 20.717 14.5193 21.1845 13.9293 21.5084C13.3394 21.8324 12.6772 22.0022 12.0042 22.0022C11.3312 22.0022 10.669 21.8324 10.0791 21.5084C9.48914 21.1845 8.99045 20.717 8.62922 20.1491C7.97205 20.2965 7.28832 20.2755 6.64142 20.0881C5.99453 19.9008 5.40541 19.5531 4.92868 19.0774C4.45196 18.6017 4.10308 18.0133 3.91437 17.3668C3.72567 16.7203 3.70326 16.0366 3.84922 15.3791C3.27917 15.0184 2.80963 14.5193 2.48426 13.9283C2.1589 13.3374 1.98828 12.6737 1.98828 11.9991C1.98828 11.3245 2.1589 10.6609 2.48426 10.0699C2.80963 9.47895 3.27917 8.97988 3.84922 8.61912Z" stroke="#BA0C2F" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M11.1225 7.69005C11.1886 7.48739 11.3177 7.31114 11.491 7.18702C11.6643 7.0629 11.8727 6.9974 12.0858 7.00008C12.299 7.00276 12.5057 7.07348 12.6758 7.20192C12.8459 7.33035 12.9706 7.50979 13.0315 7.71405L13.7685 9.16605C13.8402 9.30721 13.9445 9.42931 14.0726 9.52232C14.2007 9.61533 14.3491 9.67659 14.5055 9.70105L16.1395 9.95705C16.3499 9.95788 16.5547 10.025 16.7247 10.149C16.8948 10.273 17.0213 10.4474 17.0865 10.6475C17.1516 10.8475 17.152 11.0631 17.0875 11.2634C17.0231 11.4636 16.8971 11.6385 16.7275 11.7631L15.5555 12.9311C15.4433 13.0428 15.3592 13.1795 15.3102 13.3301C15.2612 13.4806 15.2486 13.6407 15.2735 13.7971L15.5325 15.4101C15.6038 15.6122 15.6082 15.8319 15.5451 16.0368C15.482 16.2417 15.3547 16.4208 15.1821 16.5479C15.0094 16.6749 14.8005 16.7431 14.5862 16.7424C14.3718 16.7418 14.1633 16.6722 13.9915 16.5441L12.5265 15.7941C12.3854 15.7217 12.2291 15.684 12.0705 15.684C11.9119 15.684 11.7556 15.7217 11.6145 15.7941L10.1495 16.5441C9.9777 16.6711 9.76968 16.7399 9.55597 16.7401C9.34225 16.7403 9.13408 16.6721 8.96197 16.5454C8.78987 16.4187 8.66288 16.2402 8.59963 16.036C8.53638 15.8319 8.5402 15.6129 8.61052 15.4111L8.86852 13.7981C8.89359 13.6415 8.8811 13.4813 8.83207 13.3305C8.78304 13.1798 8.69888 13.0429 8.58652 12.9311L7.43052 11.7791C7.25517 11.6576 7.12327 11.4832 7.05407 11.2814C6.98488 11.0797 6.98202 10.861 7.04591 10.6575C7.1098 10.454 7.2371 10.2763 7.40921 10.1502C7.58131 10.0242 7.78921 9.95652 8.00252 9.95705L9.63552 9.70105C9.79194 9.67659 9.94033 9.61533 10.0685 9.52232C10.1966 9.42931 10.3008 9.30721 10.3725 9.16605L11.1225 7.69005Z" stroke="#BA0C2F" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg></div><dt class="text-size-28">30+</dt><div data-wf--spacer--variant="4px" class="spacer"></div><dd class="flex-h-center mob-center gap-sm"><div class="paragraph text-weight-semibold">Years of industrial IoT experience</div></dd></dl><dl data-animate="slide-up" id="" class="margin-0"><div class="button-icon w-embed"><svg width="100%" height="100%" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M16.2461 7.76562C17.3691 8.89055 17.9998 10.4151 17.9998 12.0046C17.9998 13.5941 17.3691 15.1187 16.2461 16.2436" stroke="#BA0C2F" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M19.0742 4.9375C20.9471 6.81253 21.9991 9.35433 21.9991 12.0045C21.9991 14.6547 20.9471 17.1965 19.0742 19.0715" stroke="#BA0C2F" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M4.92487 19.0715C3.05199 17.1965 2 14.6547 2 12.0045C2 9.35433 3.05199 6.81253 4.92487 4.9375" stroke="#BA0C2F" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M7.75372 16.2436C6.63073 15.1187 6 13.5941 6 12.0046C6 10.4151 6.63073 8.89055 7.75372 7.76562" stroke="#BA0C2F" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M12 14C13.1046 14 14 13.1046 14 12C14 10.8954 13.1046 10 12 10C10.8954 10 10 10.8954 10 12C10 13.1046 10.8954 14 12 14Z" stroke="#BA0C2F" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg></div><dt class="text-size-28">2.4M+</dt><dd class="flex-h-center mob-center gap-sm"><div class="paragraph text-weight-semibold">Connected devices worldwide</div></dd></dl></div></div></main><footer data-wf--footer--variant="base" class="footer_wrap"><div class="footer"><div class="footer_split"><a aria-label="ORBCOMM Home" href="/" aria-current="page" class="footer_logo-link w-inline-block w--current"><img src="https://cdn.prod.website-files.com/6904e526a81cf6a05bbae250/690536d281b1ec0b83d77708_Frame%202147258270.svg" loading="lazy" alt="" class="footer_logo"/></a><ul role="list" class="footer_legal-tiles w-list-unstyled"><li id="w-node-_4a9d4ebf-3a99-3402-ffd0-b0bf793d3c33-197d027f" class="footer_legal-item-head"><div class="paragraph-14px text-weight-semibold">Legal</div></li><li class="footer_legal-item"><a href="/product-security-policy" class="paragraph text-color-dark text-style-muted-70">Product security policy</a><a href="/privacy-policy" class="paragraph text-color-dark text-style-muted-70">Privacy policy</a></li><li class="footer_legal-item"><a href="/app-privacy-policy" class="paragraph text-color-dark text-style-muted-70">Apps privacy policy</a><a href="/terms-and-conditions" class="paragraph text-color-dark text-style-muted-70">Terms and conditions</a></li></ul></div><div class="footer_divider"></div><div class="footer_bottom"><div><span>© </span><span datetime="2025" id="current-year" data="year" class="space">2025 </span><span>ORBCOMM. All rights reserved.</span></div><div class="max-width-340"><div class="paragraph-14px">ORBCOMM has never sold and will never sell data acquired by your visit to this website to any third party.</div></div></div></div><div class="w-embed w-iframe"><!-- Google Tag Manager (noscript) -->
<noscript>
  <iframe src="https://www.googletagmanager.com/ns.html?id=GTM-5KQ6KB"
  height="0" width="0" style="display:none;visibility:hidden"></iframe>
</noscript>
<!-- End Google Tag Manager (noscript) --></div></footer></div><script src="https://d3e54v103j8qbb.cloudfront.net/js/jquery-3.5.1.min.dc5e7f18c8.js?site=6904e526a81cf6a05bbae250" type="text/javascript" integrity="sha256-9/aliU8dGd2tb6OSsuzixeV4y/faTqgFtohetphbbj0=" crossorigin="anonymous"></script><script src="https://cdn.prod.website-files.com/6904e526a81cf6a05bbae250/js/orbcomm-staging.dfa9c9e0.77e64426cdc47703.js" type="text/javascript" integrity="sha384-ycrPCAEeb80B0O59Cob0mDD0/cAdyQ4nkJo4XH/4nOKlyF7aOKmU/xpPV8IPHedJ" crossorigin="anonymous"></script><script 
  src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js" 
  crossorigin="anonymous" 
  referrerpolicy="no-referrer" defer>
</script>
<script 
	src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/ScrollTrigger.min.js"  
  crossorigin="anonymous" 
  referrerpolicy="no-referrer" defer>
</script>


<script defer>
  document.addEventListener("DOMContentLoaded", () => {
    if (window.innerWidth >= 768) return;

    const menuButton = document.querySelector(".nav-menu-button");
    const navWrap = document.querySelector(".nav_menu-wrap");
    const nav = document.querySelector(".nav");
    const body = document.body;

    gsap.set(".nav-menu-line.first", { width: "20px", marginBottom: "6px", rotate: 0 });
    gsap.set(".nav-menu-line.mid", { width: "14px", marginBottom: "6px", opacity: 1 });
    gsap.set(".nav-menu-line.last", { width: "8px", marginBottom: "0px", rotate: 0 });
    gsap.set(navWrap, { display: "none", opacity: 0 });

    let menuOpen = false;

    const handleMenuToggle = () => {
      if (window.innerWidth >= 768) return;

      if (!menuOpen) {
        menuOpen = true;
        nav.classList.add("is-active");
        body.style.overflow = "hidden";
        gsap.set(navWrap, { display: "flex" });

        gsap.timeline({ defaults: { duration: 0.2, ease: "power2.inOut" } })
          .to(".nav-menu-line.first", { width: "20px", marginBottom: "-2px" })
          .to(".nav-menu-line.mid", { width: "20px", marginBottom: "0px", opacity: 0 }, "<")
          .to(".nav-menu-line.last", { width: "20px", marginBottom: "0px" }, "<")
          .to(".nav-menu-line.first", { rotate: 45 }, "<")
          .to(".nav-menu-line.last", { rotate: -45 }, "<")
          .to(navWrap, { opacity: 1, duration: 0.2 }, "<");
      } else {
        menuOpen = false;
        nav.classList.remove("is-active");
        body.style.overflow = "visible";

        gsap.timeline({ defaults: { duration: 0.2, ease: "power2.inOut" } })
          .to(navWrap, { opacity: 0, duration: 0.2 })
          .set(navWrap, { display: "none" })
          .to(".nav-menu-line.first", { rotate: 0, width: "20px", marginBottom: "6px" }, "<")
          .to(".nav-menu-line.mid", { rotate: 0, opacity: 1, width: "14px", marginBottom: "6px" }, "<")
          .to(".nav-menu-line.last", { rotate: 0, width: "8px", marginBottom: "0px" }, "<");
      }
    };

    menuButton.addEventListener("click", handleMenuToggle);

    window.addEventListener("resize", () => {
      if (window.innerWidth >= 768 && menuOpen) {
        gsap.set(navWrap, { display: "none", opacity: 0 });
        gsap.set(".nav-menu-line.first", { rotate: 0, width: "20px", marginBottom: "6px" });
        gsap.set(".nav-menu-line.mid", { rotate: 0, opacity: 1, width: "14px", marginBottom: "6px" });
        gsap.set(".nav-menu-line.last", { rotate: 0, width: "8px", marginBottom: "0px" });
        nav.classList.remove("is-active");
        body.style.overflow = "visible";
        menuOpen = false;
      }
    });
  });
</script>


<script defer>
// Update Year
function setVH(){let e=.01*window.visualViewport.height;document.documentElement.style.setProperty("--vh",`${e}px`)}setVH(),window.addEventListener("resize",setVH);const currentYear=new Date().getFullYear();document.querySelectorAll('[data="year"]').forEach(e=>{e.textContent=currentYear});
</script><script>
document.addEventListener("DOMContentLoaded", () => {
  if (window.innerWidth < 992) return;
  
  const elements = document.querySelectorAll('[data-reveal="bottom"]');
  elements.forEach(el => {
    const lines = el.innerHTML.split(/<br\s*\/?>/i);
    el.innerHTML = lines.map(line => `
      <span class="reveal-line"><span>${line}</span></span>
    `).join('');
    const spans = el.querySelectorAll('.reveal-line span');
    gsap.set(spans, { y: "100%", opacity: 0, willChange: "transform,opacity" });
    gsap.to(spans, {
      y: 0,
      opacity: 1,
      duration: 1,
      ease: "power3.out",
      stagger: 0.2,
      scrollTrigger: {
        trigger: el,
        start: "top 85%",
        once: true 
      },
      onComplete() {
        spans.forEach(span => {
          span.style.transform = "none"; 
          span.style.opacity = "1";    
          span.style.willChange = "";   
        });
      }
    });
  });
  
  const slideElements = document.querySelectorAll('[data-animate="slide-up"]');
  slideElements.forEach(el => {
    gsap.set(el, { y: 50, opacity: 0, willChange: "transform,opacity" });
    gsap.to(el, {
      y: 0,
      opacity: 1,
      duration: 1,
      ease: "power3.out",
      scrollTrigger: {
        trigger: el,
        start: "top 102%", 
        once: true 
      },
      onComplete() {
        gsap.set(el, { clearProps: "transform,opacity,willChange" });
      }
    });
  });
  const hoverCards = document.querySelectorAll('[data-hover="lift"]');
  hoverCards.forEach(card => {
    card.addEventListener('mouseenter', () => {
      gsap.to(card, {
        y: -16,
        duration: 0.4,
        ease: "power2.out"
      });
    });
    
    card.addEventListener('mouseleave', () => {
      gsap.to(card, {
        y: 0,
        duration: 0.4,
        ease: "power2.inOut"
      });
    });
  });
});
</script></body></html>