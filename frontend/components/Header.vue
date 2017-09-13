<template>
  <header>
  {{ categories }}
    <nav class="navbar navbar-toggleable-md navbar-light bg-faded">
      <button class="navbar-toggler navbar-toggler-right" type="button" data-toggle="collapse" data-target="#navToggle" aria-controls="navToggle" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <a class="navbar-brand" :href="baseUrl" :title="title">
        <img src="~/assets/logo/logo.png" width="30" height="30" class="d-inline-block align-top" :alt="title">
        {{ title }}
      </a>

      <div class="collapse navbar-collapse" id="navToggle">
        <ul class="navbar-nav mr-auto">
          <li class="nav-item dropdown">
            <a class="nav-link dropdown-toggle" :href="baseUrl" id="navDropdown" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
              Celebrities
            </a>
            <div class="dropdown-menu" aria-labelledby="navDropdown">
              <div v-for="cat in categories">
                <a class="dropdown-item" :href="baseUrl + keyword + '/' + cat.slug + '/'">
                  {{ cat.title }} [{{ cat.post_count }}]
                </a>
              </div>
              <hr />
              <strong><a :href="baseUrl + catKey + '/1/'" class="dropdown-item">All celebrities</a></strong>
            </div>
          </li>
          <li class="nav-item dropdown">
            <a class="nav-link dropdown-toggle" :href="baseUrl" id="navDropdownB" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
              Trending celebrity news
            </a>
            <div class="dropdown-menu" aria-labelledby="navDropdown">
              <a class="dropdown-item" :href="baseUrl + searchKey + '/death/'">Celebrity deaths</a>
              <a class="dropdown-item" :href="baseUrl + searchKey + '/hot/'">Hot celebrities</a>
              <a class="dropdown-item" :href="baseUrl + searchKey + '/famous/'">Famous celebrities</a>
              <a class="dropdown-item" :href="baseUrl + searchKey + '/black/'">Black celebrities</a>
              <a class="dropdown-item" :href="baseUrl + searchKey + '/couples/'">Celebrity couples</a>
              <a class="dropdown-item" :href="baseUrl + searchKey + '/dating/'">Celebrity dating</a>
              <a class="dropdown-item" :href="baseUrl + searchKey + '/actress/'">Actresses</a>
              <a class="dropdown-item" :href="baseUrl + searchKey + '/actor/'">Actors</a>
              <a class="dropdown-item" :href="baseUrl + searchKey + '/singer/'">Singers</a>
              <a class="dropdown-item" :href="baseUrl + searchKey + '/model/'">Models</a>
              <a class="dropdown-item" :href="baseUrl + searchKey + '/comedian/'">Comedians</a>
              <a class="dropdown-item" :href="baseUrl + searchKey + '/dancer/'">Dancers</a>
              <a class="dropdown-item" :href="baseUrl + searchKey + '/musician/'">Musicians</a>
              <a class="dropdown-item" :href="baseUrl + searchKey + '/boxer/'">Boxers</a>
              <a class="dropdown-item" :href="baseUrl + searchKey + '/writer/'">Writers</a>
              <a class="dropdown-item" :href="baseUrl + searchKey + '/football/'">Football players</a>
              <a class="dropdown-item" :href="baseUrl + searchKey + '/nasketball/'">Basketball players</a>
              <a class="dropdown-item" :href="baseUrl + searchKey + '/tennis/'">Tennis players</a>
              <a class="dropdown-item" :href="baseUrl + searchKey + '/swimmer/'">Swimmers</a>
            </div>
          </li>
        </ul>
      </div>
    </nav>
  </header>
</template>

<script>
import axios from 'axios'

export default {
  name: 'headerComponent',
  data () {
    return {
      categories: [],
      baseUrl: process.env.BASE_URL,
      title: process.env.SITE_NAME,
      keyword: process.env.KEYWORD,
      catKey: process.env.CATEGORIES_KEY,
      searchKey: process.env.SEARCH_KEYWORD
    }
  },
  asyncData ({ req, params, error }) {
    return axios.get('/cats/0/')
      .then((response) => {
        return { categories: response.data }
      })
      .catch((e) => {
        error({ statusCode: 500, message: e })
      })
  }
}
</script>