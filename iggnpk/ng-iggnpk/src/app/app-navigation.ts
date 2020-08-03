export const navigation = [
  {
    text: 'Home',
    path: 'pages/home',
    icon: 'home'
  },
  {
    text: 'Капитальный ремонт',
    icon: 'toolbox',
    permissions: 'view_notify',
    items: [
      {
        text: 'Реестр взносов',
        path: 'pages/profile'
      },
      {
        text: 'Реестр уведомлений о выбранном собственниками помещений в многоквартирном доме способе формирования фонда капитального ремонта на специальном счете',
        path: 'pages/capital-repair-notifies'
      }
    ]
  }
  ,
  {
    text: 'Администрирование',
    icon: 'preferences',
    permissions: 'view_notify',
    items: [
      {
        text: 'Пользователи',
        path: 'pages/users'
      }
    ]
  }
];
