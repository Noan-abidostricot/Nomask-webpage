import { shallowMount, mount } from '@vue/test-utils';
import SignUp from '@/components/SignUp.vue';
import ConditionList from '@/components/ConditionList.vue';
import axios from 'axios';
import flushPromises from 'flush-promises';

jest.mock('axios');

describe('SignUp.vue', () => {
  let wrapper;

  beforeEach(() => {
    wrapper = shallowMount(SignUp);
    axios.get.mockResolvedValueOnce({ data: { csrfToken: 'mocked_csrf_token' } });
  });

  it('renders correctly', () => {
    expect(wrapper.exists()).toBe(true);
    expect(wrapper.find('h2').text()).toBe('Bienvenue');
  });

  it('switches between login and signUp tabs', async () => {
    const wrapper = mount(SignUp);
    expect(wrapper.find('h2').text()).toBe('Bienvenue');
    const createAccountButton = wrapper.findAll('button').find(button => button.text() === 'Créer un compte');
    expect(createAccountButton.exists()).toBe(true);

    await createAccountButton.trigger('click');
    await wrapper.vm.$nextTick();
    expect(wrapper.find('h2').text()).toBe('Inscrivez-vous');
  });


  it('has input fields for login form', () => {
    const emailInput = wrapper.find('input[type="email"]');
    const passwordInput = wrapper.find('input[type="password"]');
    expect(emailInput.exists()).toBe(true);
    expect(passwordInput.exists()).toBe(true);
  });

  it('has input fields for signUp form', async () => {
    await wrapper.setData({ activeTab: 'signUp' });
    const firstNameInput = wrapper.find('input[type="text"]');
    const loginInput = wrapper.find('input[type="email"]');
    const passwordInput = wrapper.find('input[type="password"]');
    expect(firstNameInput.exists()).toBe(true);
    expect(loginInput.exists()).toBe(true);
    expect(passwordInput.exists()).toBe(true);
  });

  it('displays conditions component when clicking on CGU link', async () => {
    await wrapper.setData({ activeTab: 'signUp' });
    await wrapper.vm.$nextTick();
    const cguLink = wrapper.find('a.text-blue-600');
    await cguLink.trigger('click');
    expect(wrapper.vm.showConditions).toBe(true);
  });

  it('submits the form with correct data', async () => {
    await wrapper.setData({ activeTab: 'signUp' });
    axios.post.mockClear();

    await wrapper.setData({
      firstName: 'Test',
      email: 'test@example.com',
      password: 'StrongPassword123!',
      valid: true,
    });

    await wrapper.vm.checkPassword();
    await wrapper.find('form').trigger('submit.prevent');
    await flushPromises();

    expect(axios.post).toHaveBeenCalled();
    expect(axios.post).toHaveBeenCalledWith(
      `${process.env.VUE_APP_API_URL}/api/sign-up/`,
      {
        first_name: 'Test',
        email: 'test@example.com',
        password: 'StrongPassword123!',
        valid: true,
      },
      {
        withCredentials: true,
        headers: {
          'X-CSRFToken': 'mocked_csrf_token'
        }
      }
    );
  });

  it('shows success message on successful submission', async () => {
    await wrapper.setData({ activeTab: 'signUp' });
    axios.post.mockResolvedValueOnce({ status: 201 });
    await wrapper.setData({
      first_name: 'Test',
      email: 'test@example.com',
      password: 'StrongPassword123!',
      valid: true,
    });
    await wrapper.vm.checkPassword();
    await wrapper.find('form').trigger('submit.prevent');
    await flushPromises();

    expect(wrapper.vm.registrationSuccess).toBe(true);
    expect(wrapper.find('h2.text-2xl.font-bold.mb-4').text()).toBe('Félicitations !');
  });

  it('shows error message on failed submission', async () => {
    await wrapper.setData({ activeTab: 'signUp' });
    axios.post.mockRejectedValueOnce(new Error('Erreur lors de l\'inscription'));
    await wrapper.setData({
      first_name: 'Test',
      email: 'test@example.com',
      password: 'StrongPassword123!',
      valid: true,
    });
    await wrapper.vm.checkPassword();
    await wrapper.find('form').trigger('submit.prevent');
    await flushPromises();

    expect(wrapper.vm.errorMessage).toContain("Une erreur est survenue lors de l'inscription.");
  });

  it('sets currentVersion to 0 when there are no conditions', async () => {
    axios.get.mockResolvedValueOnce({ data: [] });

    const wrapper = mount(SignUp);
    await flushPromises();
    await wrapper.setData({ activeTab: 'signUp', showConditions: true });
    await wrapper.vm.$nextTick();

    const conditionList = wrapper.findComponent(ConditionList);
    await conditionList.vm.$nextTick();
    expect(conditionList.vm.currentVersion).toBe(0);
  });

  it('displays a message when there are no conditions', async () => {
    axios.get.mockResolvedValueOnce({ data: [] });
    const wrapper = mount(SignUp, {
        data() {
            return {
                showConditions: true,
                activeTab: 'signUp'
            }
        }
    });
    await flushPromises();
    const conditionList = wrapper.findComponent(ConditionList);
    await conditionList.vm.$nextTick();
    const noConditionsMessage = conditionList.find('#no-conditions');
    expect(noConditionsMessage.exists()).toBe(true);
    expect(noConditionsMessage.text()).toContain("Aucune condition à afficher. Vous pouvez toujours vous inscrire.");
  });

  it('validates password strength', async () => {
    await wrapper.setData({ activeTab: 'signUp' });
    const passwordInput = wrapper.find('input[type="password"]');

    await passwordInput.setValue('-');
    await passwordInput.trigger('input');

    expect(wrapper.vm.passwordErrors).toContain("Au moins 10 caractères");
    expect(wrapper.vm.passwordErrors).toContain("Au moins une majuscule");
    expect(wrapper.vm.passwordErrors).toContain("Au moins une minuscule");
    expect(wrapper.vm.passwordErrors).toContain("Au moins un chiffre");
    expect(wrapper.vm.isPasswordValid).toBe(false);

    await passwordInput.setValue('StrongPassword123!');
    await passwordInput.trigger('input');

    expect(wrapper.vm.passwordErrors).toHaveLength(0);
    expect(wrapper.vm.isPasswordValid).toBe(true);

    await wrapper.setData({ password: '-', valid: true });
    await wrapper.vm.checkPassword();
    await wrapper.vm.$nextTick();
    expect(wrapper.find('button[type="submit"]').element.disabled).toBe(true);

    await wrapper.setData({ password: 'StrongPassword123!', valid: true });
    await wrapper.vm.checkPassword();
    await wrapper.vm.$nextTick();
    expect(wrapper.find('button[type="submit"]').element.disabled).toBe(false);
  });

  it('properly manages a 403 error (potentially linked to the CSRF)', async () => {
    axios.post.mockRejectedValueOnce({
      response: {
        status: 403,
        data: { detail: "Accès refusé. Veuillez réessayer." }
      }
    });

    await wrapper.setData({
      activeTab: 'signUp',
      first_name: 'Test',
      email: 'test@example.com',
      password: 'StrongPassword123!',
      valid: true,
    });

    await wrapper.vm.$nextTick();
    await wrapper.vm.checkPassword();
    await wrapper.find('form').trigger('submit.prevent');
    await flushPromises();

    expect(axios.post).toHaveBeenCalled();
    expect(wrapper.vm.errorMessage).toBe("Accès refusé. Veuillez réessayer.");

    const lastCall = axios.post.mock.calls[0];
    expect(lastCall[2].headers).toHaveProperty('X-CSRFToken');
  });
});
