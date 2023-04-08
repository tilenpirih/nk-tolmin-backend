import json
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from datetime import datetime
from pathlib import Path
import shutil
from urllib.parse import quote, unquote
from flask import request
from flask_restful import Resource
from playhouse.shortcuts import model_to_dict
from schema import Article
from peewee import fn
from math import ceil

class GetArticle(Resource):
    def get(self, article_id):
        article = Article.get_by_id(article_id)
        model = model_to_dict(article)
        model["created"] = model["created"].isoformat()
        model["updated"] = model["updated"].isoformat()
        return model

class GetArticles(Resource):
    def get(self, page):
        numArticles = Article.select().where(Article.visible == True).count()
        numPages = ceil(numArticles / 12)
        if page > numPages:
            page = numPages
        articles = Article.select(Article.title, Article.preview, Article.created, Article.thumbnail, Article.article_id).where(Article.visible == True).order_by(Article.updated.desc()).paginate(page, 12)
        for article in articles:
            article.created = article.created.isoformat()
        obj = {}
        obj["articles"] = [model_to_dict(article, fields_from_query=articles) for article in articles]
        obj["page"] = page
        obj["pages"] = numPages
        return obj

class GetAllArticles(Resource):
    def get(self):
        articles = Article.select(Article.title, Article.preview, Article.created, Article.thumbnail, Article.article_id).order_by(Article.updated.desc())
        for article in articles:
            article.created = article.created.isoformat()
        return [model_to_dict(article, fields_from_query=articles) for article in articles]

class AddImagesArticle(Resource):
    def post(self, article_id):
        article = Article.get_by_id(article_id)
        images = request.files.getlist('images')
        image_paths = [] if article.images is None else article.images
        for image in images:
            file = Path(f'./assets/articles/{article_id}/{image.filename}')
            if not file.exists():
                image.save(os.path.join(f'./assets/articles/{article_id}', f'{image.filename}'))
                image_path = f"assets/articles/{article_id}/{quote(image.filename)}"
                image_paths.append(image_path)
        article.images = image_paths
        article.save()
        model = Article.get_by_id(article_id)
        model = model_to_dict(article)
        model["created"] = model["created"].isoformat()
        model["updated"] = model["updated"].isoformat()
        return model

class CreateArticle(Resource):
    def post(self):
        maxID = Article.select(fn.Max(Article.article_id)).scalar()
        if maxID is None:
            maxID = 0
        Path(f'./assets/articles/{maxID+1}').mkdir(parents=True, exist_ok=True)
        Article.create(article_id=maxID+1)
        return {"article_id": maxID+1}


class UpdateArticle(Resource):
    # Todo check if gallery_images exist
    def post(self, article_id):
        title = request.form.get('title')
        content = request.form.get('content')
        visible = request.form.get('visible') in ['true', 'True']
        thumbnail = request.form.get('thumbnail')
        preview = request.form.get('preview')
        gallery_images = json.loads(request.form.get('gallery_images'))
        gallery_images = None if gallery_images == [] or gallery_images == "null" else gallery_images
        preview = None if preview == "null" else preview
        thumbnail = None if thumbnail == "null" else thumbnail
        title = None if title == "null" else title
        thumbnail = None if thumbnail == "null" else thumbnail
        query = model_to_dict(Article.get_by_id(article_id))
        updated = datetime.now()
        created = query["created"]
        created = updated if query["visible"] == False and visible == True else created
        Article.update(title=title, content=content, visible=visible, thumbnail=thumbnail, gallery_images=gallery_images, preview=preview, created=created, updated=updated).where(Article.article_id == article_id).execute()
        query = model_to_dict(Article.get_by_id(article_id))
        query["created"] = query["created"].isoformat()
        query["updated"] = query["updated"].isoformat()
        return query

class DeleteImage(Resource):
    def delete(self, article_id):
        article = Article.get_by_id(article_id)
        path = request.args.get('path')
        if not os.path.exists(unquote(path)):
            return "image not found", 400
        os.remove(unquote(path))
        if quote(path) in article.images: article.images.remove(quote(path))
        if article.gallery_images != None and quote(path) in article.gallery_images: article.gallery_images.remove(quote(path))
        article.save()
        
        query = model_to_dict(Article.get_by_id(article_id))
        query["created"] = query["created"].isoformat()
        query["updated"] = query["updated"].isoformat()
        return query

class DeleteArticle(Resource):
    def post(self, article_id):
        try:
            article = Article.get(Article.article_id == article_id).get()
        except Article.DoesNotExist:
            return "Article not found", 400
        article.delete_instance()
        shutil.rmtree(f'./assets/articles/{article_id}')
        return "deleted"