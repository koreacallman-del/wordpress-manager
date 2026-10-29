<?php
/**
 * Fermentpedia Child Theme — functions.php
 *
 * 1. 부모 테마 + 차일드 CSS 로드
 * 2. 고정 헤더 (sticky header) JS
 * 3. 프론트페이지 Kadence 히어로 제거
 * 4. 메인페이지 랜덤 피처드 포스트 2개
 * 5. 글 레이아웃: 이미지·제목 겹침 제거
 */

defined('ABSPATH') || exit;

/* ---------- 1. 스타일 로드 ---------- */

add_action('wp_enqueue_scripts', function () {
    wp_enqueue_style(
        'kadence-parent',
        get_template_directory_uri() . '/style.css'
    );
    wp_enqueue_style(
        'fermentpedia-child',
        get_stylesheet_uri(),
        ['kadence-parent'],
        wp_get_theme()->get('Version')
    );
});

/* ---------- 1b. 성능 최적화 ---------- */

// DNS prefetch / preconnect for Google Fonts
add_action('wp_head', function () {
    echo '<link rel="preconnect" href="https://fonts.googleapis.com" crossorigin>' . "\n";
    echo '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>' . "\n";
}, 1);

// font-display: swap 강제 (Google Fonts FOIT 방지 → CLS 개선)
add_filter('style_loader_tag', function ($html, $handle) {
    if (strpos($html, 'fonts.googleapis.com') !== false && strpos($html, 'display=swap') === false) {
        $html = str_replace('googleapis.com/css2?', 'googleapis.com/css2?display=swap&', $html);
        $html = str_replace('googleapis.com/css?', 'googleapis.com/css?display=swap&', $html);
    }
    return $html;
}, 10, 2);

// 이미지에 width/height 속성 누락 시 추가 (CLS 방지)
add_filter('wp_get_attachment_image_attributes', function ($attr, $attachment) {
    if (empty($attr['width']) || empty($attr['height'])) {
        $meta = wp_get_attachment_metadata($attachment->ID);
        if ($meta && !empty($meta['width']) && !empty($meta['height'])) {
            $attr['width'] = $meta['width'];
            $attr['height'] = $meta['height'];
        }
    }
    return $attr;
}, 10, 2);

// 비필수 JS를 defer로 로드 (렌더 블로킹 제거)
add_filter('script_loader_tag', function ($tag, $handle) {
    $no_defer = ['jquery-core', 'jquery-migrate', 'wp-hooks'];
    if (is_admin() || in_array($handle, $no_defer)) return $tag;
    if (strpos($tag, 'defer') !== false || strpos($tag, 'async') !== false) return $tag;
    return str_replace(' src=', ' defer src=', $tag);
}, 10, 2);


/* ---------- 2. 고정 헤더 JS ---------- */

add_action('wp_footer', function () {
    ?>
    <script>
    (function() {
        var header = document.querySelector('header.site-header');
        if (!header) return;

        var last = 0;
        var ticking = false;

        function onScroll() {
            last = window.scrollY;
            if (!ticking) {
                window.requestAnimationFrame(function() {
                    header.classList.toggle('is-sticky', last > 10);
                    ticking = false;
                });
                ticking = true;
            }
        }

        window.addEventListener('scroll', onScroll, { passive: true });
        onScroll();
    })();
    </script>
    <?php
});


/* ---------- 3. 프론트페이지 빈 공간 제거 ---------- */

add_filter('kadence_show_hero_title', function ($show) {
    if (is_front_page()) return false;
    return $show;
});

add_action('wp_head', function () {
    if (!is_front_page()) return;
    ?>
    <style>
        .home #inner-wrap {
            padding-top: 0 !important;
            margin-top: 0 !important;
        }
    </style>
    <?php
});

/* ---------- 4. 메인페이지 랜덤 피처드 포스트 (AJAX) ---------- */

// 4a. AJAX 엔드포인트 — 랜덤 카드 HTML 반환
add_action('wp_ajax_fp_random_cards', 'fp_random_cards_ajax');
add_action('wp_ajax_nopriv_fp_random_cards', 'fp_random_cards_ajax');

function fp_random_cards_ajax() {
    header('Cache-Control: no-cache, no-store, must-revalidate');
    header('Pragma: no-cache');

    $all = get_posts([
        'numberposts'  => 30,
        'post_status'  => 'publish',
        'meta_key'     => '_thumbnail_id',
        'orderby'      => 'date',
        'order'        => 'DESC',
    ]);

    if (count($all) < 2) { wp_die(); }

    shuffle($all);
    $picks = array_slice($all, 0, 2);

    foreach ($picks as $p) :
        $img = get_the_post_thumbnail_url($p->ID, 'large');
        $cat = get_the_category($p->ID);
        $cat_name = !empty($cat) ? esc_html($cat[0]->name) : '';
    ?>
    <a href="<?php echo get_permalink($p->ID); ?>" class="fp-featured-card">
        <div class="fp-featured-img" style="background-image:url('<?php echo esc_url($img); ?>')"></div>
        <div class="fp-featured-info">
            <?php if ($cat_name) : ?>
                <span class="fp-featured-cat"><?php echo $cat_name; ?></span>
            <?php endif; ?>
            <h3 class="fp-featured-title"><?php echo esc_html($p->post_title); ?></h3>
        </div>
    </a>
    <?php endforeach;
    wp_die();
}

// 4b. 프론트페이지에 빈 카드 컨테이너 + AJAX 로드 스크립트
add_action('wp_footer', function () {
    if (!is_front_page()) return;
    $ajax_url = admin_url('admin-ajax.php');
    ?>
    <div id="fp-featured-pending" style="display:none">
        <div class="fp-featured-wrap">
            <div class="fp-featured-grid" id="fp-featured-grid"></div>
        </div>
    </div>
    <script>
    (function() {
        var pending = document.getElementById('fp-featured-pending');
        var target = document.getElementById('inner-wrap');
        if (!pending || !target) return;
        var wrap = pending.querySelector('.fp-featured-wrap');
        if (!wrap) return;
        var firstChild = target.firstElementChild;
        if (firstChild) {
            firstChild.insertAdjacentElement('afterend', wrap);
        } else {
            target.insertBefore(wrap, target.firstChild);
        }
        pending.remove();

        var grid = document.getElementById('fp-featured-grid');
        var xhr = new XMLHttpRequest();
        xhr.open('GET', '<?php echo esc_js($ajax_url); ?>?action=fp_random_cards&_=' + Date.now(), true);
        xhr.onload = function() {
            if (xhr.status === 200 && xhr.responseText.trim()) {
                grid.innerHTML = xhr.responseText;
            }
        };
        xhr.send();

        var kids = target.children;
        for (var i = 0; i < kids.length; i++) {
            var el = kids[i];
            if (el.classList.contains('fp-featured-wrap')) continue;
            var rect = el.getBoundingClientRect();
            var text = (el.textContent || '').trim();
            if (rect.height > 20 && rect.height < 300 && text.length === 0 && !el.querySelector('img, video, iframe, canvas')) {
                el.style.display = 'none';
            } else if (text.length > 0) {
                break;
            }
        }
    })();
    </script>
    <?php
});


/* ---------- 5. 글 레이아웃: 이미지·제목 겹침 제거 ---------- */

add_filter('theme_mod_post_title_layout', function () {
    return 'normal';
});

add_filter('theme_mod_post_title_inner_layout', function () {
    return 'standard';
});

add_filter('theme_mod_post_title_featured_placement', function () {
    return 'above';
});

add_filter('theme_mod_post_feature_position', function () {
    return 'above';
});

add_filter('theme_mod_post_title_element_feature', function ($val) {
    if (is_array($val)) {
        $val['enabled'] = true;
    }
    return $val;
});
