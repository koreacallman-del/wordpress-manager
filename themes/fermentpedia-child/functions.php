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


/* ---------- 3. 프론트페이지 Kadence 페이지 타이틀/히어로 완전 제거 ---------- */

// 3a. Kadence 필터로 히어로 타이틀 렌더링 차단
add_filter('kadence_show_hero_title', function ($show) {
    if (is_front_page()) return false;
    return $show;
});

// 3b. Kadence 포스트 메타를 필터링해서 페이지 타이틀 영역 비활성화
add_filter('get_post_metadata', function ($value, $post_id, $meta_key, $single) {
    if (!is_front_page()) return $value;
    if ($meta_key === '_kad_post_title') {
        return $single ? 'hide' : ['hide'];
    }
    if ($meta_key === '_kad_post_title_height') {
        return $single ? '0' : ['0'];
    }
    return $value;
}, 10, 4);

// 3c. 와일드카드 CSS — 클래스명에 hero/page-title 포함된 모든 요소 제거
add_action('wp_head', function () {
    if (!is_front_page()) return;
    ?>
    <style>
        .home [class*="hero"],
        .home [class*="page-hero"],
        .home [class*="entry-hero"],
        .home [class*="page-title"]:not(.site-title),
        .home .entry-header {
            display: none !important;
            height: 0 !important;
            min-height: 0 !important;
            max-height: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
            overflow: hidden !important;
        }
        .home .site-main,
        .home .content-wrap,
        .home .site-content,
        .home #inner-wrap,
        .home .site-container {
            padding-top: 0 !important;
            margin-top: 0 !important;
        }
    </style>
    <?php
});

// 3d. JavaScript 최종 방어 — DOM에서 빈 공간 요소를 직접 제거
add_action('wp_footer', function () {
    if (!is_front_page()) return;
    ?>
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        var wrap = document.querySelector('.fp-featured-wrap');
        if (!wrap) return;
        var all = document.querySelectorAll('body > *, body > div > *');
        for (var i = 0; i < all.length; i++) {
            var el = all[i];
            if (el.tagName === 'HEADER' || el.tagName === 'FOOTER' || el.tagName === 'MAIN') continue;
            if (el.classList.contains('fp-featured-wrap')) continue;
            if (el.querySelector && el.querySelector('main, footer, .fp-featured-wrap')) continue;
            if (el.querySelector && el.querySelector('.site-main')) continue;
            var cls = el.className || '';
            if (typeof cls === 'string' && (cls.indexOf('hero') !== -1 || cls.indexOf('page-title') !== -1 || cls.indexOf('entry-header') !== -1)) {
                el.style.cssText = 'display:none!important;height:0!important;';
            }
        }
        var header = document.querySelector('header.site-header');
        if (!header) return;
        var next = wrap.nextElementSibling;
        while (next) {
            if (next.tagName === 'MAIN' || next.id === 'main' || next.classList.contains('site-main')) break;
            if (next.querySelector && next.querySelector('main, .site-main, #main')) break;
            var rect = next.getBoundingClientRect();
            var text = (next.textContent || '').trim();
            if (rect.height > 30 && text.length < 5 && !next.querySelector('img, video, canvas')) {
                next.style.cssText = 'display:none!important;';
            }
            next = next.nextElementSibling;
        }
    });
    </script>
    <?php
});


/* ---------- 4. 메인페이지 랜덤 피처드 포스트 ---------- */

add_action('kadence_after_header', function () {
    if (!is_front_page()) {
        return;
    }

    $all = get_posts([
        'numberposts'  => 30,
        'post_status'  => 'publish',
        'meta_key'     => '_thumbnail_id',
        'orderby'      => 'date',
        'order'        => 'DESC',
    ]);

    if (count($all) < 2) {
        return;
    }

    shuffle($all);
    $picks = array_slice($all, 0, 2);
    ?>
    <div class="fp-featured-wrap">
        <div class="fp-featured-grid">
            <?php foreach ($picks as $p) :
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
            <?php endforeach; ?>
        </div>
    </div>
    <?php
}, 5);


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
