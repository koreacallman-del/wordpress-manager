<?php
/**
 * Fermentpedia Child Theme — functions.php
 *
 * 1. 부모 테마 + 차일드 CSS 로드
 * 2. 고정 헤더 (sticky header) JS
 * 3. 프론트페이지 Kadence 히어로 제거
 * 4. 메인페이지 피처드 포스트 (서버 렌더링)
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

/* ---------- 4. 메인페이지 피처드 포스트 (서버 렌더링) ---------- */

function fp_render_featured_section() {
    if (!is_front_page()) return;

    $all = get_posts([
        'numberposts'  => 30,
        'post_status'  => 'publish',
        'meta_key'     => '_thumbnail_id',
        'orderby'      => 'date',
        'order'        => 'DESC',
    ]);

    if (count($all) < 2) return;

    shuffle($all);
    $picks = array_slice($all, 0, 2);

    $cap_srcset = function ($sources) {
        foreach ($sources as $w => $source) {
            if ($w > 1024) unset($sources[$w]);
        }
        return $sources;
    };
    add_filter('wp_calculate_image_srcset', $cap_srcset);
    ?>
    <section class="fp-featured-wrap" aria-label="Featured">
        <h2 class="fp-featured-heading">Featured</h2>
        <div class="fp-featured-grid">
        <?php foreach ($picks as $i => $p) :
            $thumb_id = get_post_thumbnail_id($p->ID);
            $cat = get_the_category($p->ID);
            $cat_name = !empty($cat) ? esc_html($cat[0]->name) : '';

            $img_attrs = [
                'class'    => 'fp-featured-img-el',
                'sizes'    => '(max-width: 768px) 100vw, 560px',
                'decoding' => 'async',
            ];

            if ($i === 0) {
                $img_attrs['loading']       = 'eager';
                $img_attrs['fetchpriority'] = 'high';
            } else {
                $img_attrs['loading'] = 'lazy';
            }
        ?>
            <a href="<?php echo esc_url(get_permalink($p->ID)); ?>" class="fp-featured-card">
                <div class="fp-featured-img">
                    <?php echo wp_get_attachment_image($thumb_id, 'large', false, $img_attrs); ?>
                </div>
                <div class="fp-featured-info">
                    <?php if ($cat_name) : ?>
                        <span class="fp-featured-cat"><?php echo $cat_name; ?></span>
                    <?php endif; ?>
                    <h3 class="fp-featured-title"><?php echo esc_html($p->post_title); ?></h3>
                </div>
            </a>
        <?php endforeach; ?>
        </div>
    </section>
    <?php
    remove_filter('wp_calculate_image_srcset', $cap_srcset);
}
add_action('kadence_after_header', 'fp_render_featured_section');

// 프론트페이지 빈 공간(히어로 잔여 div) 정리
add_action('wp_footer', function () {
    if (!is_front_page()) return;
    ?>
    <script>
    (function() {
        var target = document.getElementById('inner-wrap');
        if (!target) return;
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
