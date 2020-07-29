export const navigation = [
  {
    text: 'Home',
    path: '/home',
    icon: 'home'
  },
  {
    text: 'Капитальный ремонт',
    icon: 'toolbox',
    items: [
      {
        text: 'Реестр взносов',
        path: '/profile'
      },
      {
        text: 'Реестр уведомлений о выбранном собственниками помещений в многоквартирном доме способе формирования фонда капитального ремонта на специальном счете',
        path: 'pages/capital-repair-notifies'
      }
    ]
  }
];
