import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

// The specification is the product of this repository; the checker in
// rolecheck/ is what enforces it. They ship together so that a rule and its
// enforcement can be made to agree -- not so that they already do. The checker
// still hardcodes what the rules state, and FLOOR-01 is the standing example:
// rolecheck.structure.TEMPLATE_FLOOR is 2.18 where the rule says 2.21.
const config: Config = {
  title: "Ansible Style Guide",
  tagline: "The rules, and the checker that enforces them",
  favicon: 'img/favicon.svg',

  url: 'https://nwarila-platform.github.io',
  baseUrl: '/ansible-style-guide/',
  organizationName: 'nwarila-platform',
  projectName: 'ansible-style-guide',
  trailingSlash: false,

  // A broken cross-reference between rules is a defect, not a warning: rules
  // cite each other by id and a dead link means a rule points at nothing.
  onBrokenLinks: 'throw',

  markdown: {
    mermaid: true,
    hooks: {onBrokenMarkdownLinks: 'throw'},
  },
  themes: ['@docusaurus/theme-mermaid'],

  presets: [
    [
      'classic',
      {
        docs: {
          routeBasePath: '/',
          sidebarPath: './sidebars.ts',
          editUrl:
            'https://github.com/nwarila-platform/ansible-style-guide/tree/main/',
          showLastUpdateTime: true,
          showLastUpdateAuthor: true,
        },
        blog: false,
        theme: {customCss: './src/css/custom.css'},
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    navbar: {
      title: 'Ansible Style Guide',
      items: [
        {type: 'docSidebar', sidebarId: 'spec', position: 'left', label: 'Specification'},
        {to: '/enforcement', label: 'Enforcement', position: 'left'},
        {to: '/migration-order', label: 'Migration', position: 'left'},
        {
          href: 'https://github.com/nwarila-platform/ansible-style-guide',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      copyright:
        'Ansible Style Guide — nwarila-platform. The checker that enforces this lives in the same repository.',
    },
    prism: {additionalLanguages: ['yaml', 'bash', 'python', 'powershell']},
    tableOfContents: {minHeadingLevel: 2, maxHeadingLevel: 4},
  } satisfies Preset.ThemeConfig,
};

export default config;
