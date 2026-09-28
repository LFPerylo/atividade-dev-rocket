import type { Preview } from '@storybook/react-vite'

import '../src/index.css'

const preview: Preview = {
  parameters: {
    layout: 'centered',
    backgrounds: { disable: true },
    controls: { expanded: true },
  },
  decorators: [
    (Story) => (
      <div className="bg-ink-900 p-6 text-ink-200">
        <Story />
      </div>
    ),
  ],
}

export default preview
