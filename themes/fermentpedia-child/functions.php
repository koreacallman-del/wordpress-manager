<?php
/**
 * Fermentpedia Child Theme — functions.php
 *
 * 1. 부모 테마 + 차일드 CSS 로드
 * 2. 고정 헤더 (sticky header) JS
 * 3. 메인페이지 랜덤 히어로 이미지
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


/* ---------- 3. 메인페이지 랜덤 히어로 ---------- */

add_action('kadence_after_header', function () {
    if (!is_front_page()) {
        return;
    }

    $images = fp_get_hero_images();
    if (empty($images)) {
        return;
    }

    $pick = $images[array_rand($images)];
    ?>
    <section class="fp-hero" style="background-image:url('<?php echo esc_url($pick); ?>')">
        <div class="fp-hero-content">
            <h1 class="fp-hero-title"><?php bloginfo('name'); ?></h1>
            <p class="fp-hero-subtitle"><?php bloginfo('description'); ?></p>
        </div>
    </section>
    <?php
});


/**
 * 히어로 이미지 후보 목록 가져오기
 *
 * 우선순위:
 *  1) 커스터마이저에서 설정한 fp_hero_images (쉼표 구분 URL)
 *  2) 최근 발행 글 중 특성 이미지가 있는 것 최대 15개
 *
 * 결과는 1시간 캐시.
 */
function fp_get_hero_images() {
    $cached = get_transient('fp_hero_images');
    if (is_array($cached) && !empty($cached)) {
        return $cached;
    }

    // 커스터마이저 설정 (선택 사항)
    $custom = get_theme_mod('fp_hero_images', '');
    if (!empty($custom)) {
        $urls = array_filter(array_map('trim', explode(',', $custom)));
        if (!empty($urls)) {
            set_transient('fp_hero_images', $urls, HOUR_IN_SECONDS);
            return $urls;
        }
    }

    // 특성 이미지에서 자동 수집
    $posts = get_posts([
        'numberposts'  => 30,
        'post_status'  => 'publish',
        'meta_key'     => '_thumbnail_id',
        'orderby'      => 'date',
        'order'        => 'DESC',
    ]);

    $images = [];
    foreach ($posts as $p) {
        $url = get_the_post_thumbnail_url($p->ID, 'full');
        if ($url) {
            $images[] = $url;
        }
        if (count($images) >= 15) {
            break;
        }
    }

    if (!empty($images)) {
        set_transient('fp_hero_images', $images, HOUR_IN_SECONDS);
    }

    return $images;
}


/* ---------- 4. 글 레이아웃: 이미지·제목 겹침 제거 ---------- */

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


/* ---------- 5. 커스터마이저 설정 (히어로 이미지 URL) ---------- */

add_action('customize_register', function ($wp_customize) {
    $wp_customize->add_section('fp_hero_section', [
        'title'    => 'Fermentpedia Hero',
        'priority' => 35,
    ]);

    $wp_customize->add_setting('fp_hero_images', [
        'default'           => '',
        'sanitize_callback' => 'sanitize_textarea_field',
        'transport'         => 'refresh',
    ]);

    $wp_customize->add_control('fp_hero_images', [
        'label'       => 'Hero Image URLs',
        'description' => '쉼표로 구분된 이미지 URL. 비워두면 최근 글 특성 이미지를 자동으로 사용합니다.',
        'section'     => 'fp_hero_section',
        'type'        => 'textarea',
    ]);
});
