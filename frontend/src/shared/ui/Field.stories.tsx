import type { Meta, StoryObj } from '@storybook/react-vite'

import { Field, Input, Select, TextArea } from '@/shared/ui/Field'

const meta = {
  title: 'UI/Field',
  component: Field,
  args: { id: 'campo', label: 'Título', children: null },
} satisfies Meta<typeof Field>

export default meta
type Story = StoryObj<typeof meta>

export const TextInput: Story = {
  render: (args) => (
    <Field {...args}>
      <Input id={args.id} placeholder="Oppenheimer" />
    </Field>
  ),
}

export const WithError: Story = {
  args: { error: 'Informe o título' },
  render: (args) => (
    <Field {...args}>
      <Input id={args.id} invalid />
    </Field>
  ),
}

export const WithHint: Story = {
  args: { id: 'diretores', label: 'Diretores', hint: 'Separe vários nomes por vírgula' },
  render: (args) => (
    <Field {...args}>
      <Input id={args.id} />
    </Field>
  ),
}

export const Multiline: Story = {
  args: { id: 'sinopse', label: 'Sinopse' },
  render: (args) => (
    <Field {...args}>
      <TextArea id={args.id} rows={4} />
    </Field>
  ),
}

export const Dropdown: Story = {
  args: { id: 'genero', label: 'Gênero' },
  render: (args) => (
    <Field {...args}>
      <Select id={args.id}>
        <option>Drama</option>
        <option>Crime</option>
      </Select>
    </Field>
  ),
}
